# -*- coding: UTF-8 -*-

from maeve.api import Api
from maeve.models import Character, Account, WalletTransaction, MarketOrder, ItemTypeIndex, ItemStats
from google.appengine.ext import ndb
from datetime import datetime
from google.appengine.api import taskqueue
import logging


@ndb.tasklet
def get_characters_async():
  characters = yield Character.query().fetch_async()
  raise ndb.Return(characters)


@ndb.tasklet
def get_accounts_async():
  accounts = yield Account.query().fetch_async()
  raise ndb.Return(accounts)


def get_characters_and_accounts():
  yield get_characters_async(), get_accounts_async()


def get_latest_transaction(character):
  if not character.last_transaction_key:
    raise ndb.Return((character.key, None))
  else:
    transaction = yield ndb.get_async(character.last_transaction_key)
    raise ndb.Return((character.key, transaction))


def update_item_index(new_values):
  logging.info('Item index being updated')
  item_index = ItemTypeIndex.query().get()
  if not item_index:
    item_index = ItemTypeIndex()
  item_index.items.update(new_values)
  item_index.put()


def index_all_characters():

  characters = Character.query(Character.active == True)
  task_count = 0
  for character in characters:
    task_count += 1
    taskqueue.add(url='/_task/sync',
                  params={'char': character.key.urlsafe()},
                  queue_name='transaction-sync',
                  )

  logging.info('{0} sync tasks enqueued'.format(task_count))


def index_character(character, account):

  try:
    logging.info('Synching: Character {0} / {1}'.format(character.name, character.char_id))
    item_stats = ItemStats.query(ItemStats.character_key == character.key).fetch_async()
    orders = MarketOrder.query(MarketOrder.character_key == character.key).fetch_async()

    api = Api(account.api_id, account.api_vcode)
    api.authenticate()
    api_char = api.get_character(character.char_id)

    row_count = 250
    all_items = {}

    character.last_update = datetime.now()

    last_transaction_id = character.last_transaction_id
    last_transaction_date = character.last_transaction_date

    api_wallet_transactions = api_char.WalletTransactions(rowCount=(last_transaction_id is None and 1000 or row_count))
    item_stats = dict([(i.type_id, i) for i in item_stats.get_result()])

    newest_transaction, oldest_transaction, items = sync_transactions(character,
                                                               api_wallet_transactions,
                                                               last_transaction_id,
                                                               last_transaction_date,
                                                               item_stats)

    all_items.update(items or {})

    while last_transaction_id and last_transaction_date and oldest_transaction and \
    (datetime.fromtimestamp(oldest_transaction.transactionDateTime) > last_transaction_date or oldest_transaction.transactionID > last_transaction_id):
      logging.info('Fetching another batch from id {0}'.format(oldest_transaction.transactionID))

      api_wallet_transactions = api_char.WalletTransactions(rowCount=row_count, fromID=oldest_transaction.transactionID)
      newest_transaction, oldest_transaction, items = sync_transactions(character,
                                                                 api_wallet_transactions,
                                                                 last_transaction_id,
                                                                 last_transaction_date,
                                                                 item_stats)

      all_items.update(items or {})

    sync_orders(character,
                api_char.MarketOrders(),
                orders.get_result())

    character.put_async()
    logging.info('Syncing done: Character {0} / {1}'.format(character.name, character.char_id))
    return all_items
  except:
    import traceback
    logging.error('Error while syncing character {0} / {1}'.format(character.name, character.char_id))
    logging.error(traceback.format_exc())
    return None


def sync_transactions(character,
                      api_wallet_transactions,
                      last_transaction_id,
                      last_transaction_date,
                      item_stats):

  newest_transaction, oldest_transaction, items = None, None, {}
  to_put = []

  for row in api_wallet_transactions.transactions:
    if (not last_transaction_id and not last_transaction_date) or \
    datetime.fromtimestamp(row.transactionDateTime) > last_transaction_date or row.transactionID > last_transaction_id:

      wt = WalletTransaction(character_key=character.key,
                             char_id=character.char_id,
                             transaction_id=row.transactionID,
                             transaction_date=datetime.fromtimestamp(row.transactionDateTime),
                             quantity=int(row.quantity),
                             type_name=row.typeName,
                             type_id=str(row.typeID),
                             unit_price=float(row.price),
                             client_id=str(row.clientID),
                             client_name=str(row.clientName),
                             transaction_type=(row.transactionType == 'sell' and WalletTransaction.SELL or WalletTransaction.BUY),
                             journal_transaction_id=str(row.journalTransactionID))

      to_put.append(wt)
      items[wt.type_id] = wt.type_name

      stats = item_stats.get(wt.type_id, None)
      abs_balance_change = wt.quantity * wt.unit_price

      if not stats:
        stats = ItemStats(user=character.user,
                          char_id=character.char_id,
                          character_key=character.key,
                          type_id=wt.type_id,
                          accumulated_cost=(wt.transaction_type == WalletTransaction.BUY and abs_balance_change or 0),
                          accumulated_earnings=(wt.transaction_type == WalletTransaction.SELL and abs_balance_change or 0),
                          items_bought=(wt.transaction_type == WalletTransaction.BUY and wt.quantity or 0),
                          items_sold=(wt.transaction_type == WalletTransaction.SELL and wt.quantity or 0),
                          )
        item_stats[wt.type_id] = stats
      else:
        if wt.transaction_type == WalletTransaction.BUY:
          stats.accumulated_cost += abs_balance_change
          stats.items_bought += wt.quantity
        else:
          stats.accumulated_earnings += abs_balance_change
          stats.items_sold += wt.quantity

    else:
      logging.debug('Skipped transaction {0}'.format(row.transactionID))

    if not oldest_transaction or row.transactionID < oldest_transaction.transactionID:
      oldest_transaction = row

    if not newest_transaction or row.transactionID > newest_transaction.transactionID:
      newest_transaction = row

    character.last_transaction_id = max(character.last_transaction_id, row.transactionID)
    row_date = datetime.fromtimestamp(row.transactionDateTime)
    character.last_transaction_date = character.last_transaction_date and max(character.last_transaction_date, row_date) or row_date

  ndb.put_multi_async(to_put)

  for stats in item_stats.values():
    stats.roi_yield = stats.accumulated_cost > 0 and (stats.accumulated_earnings - stats.accumulated_cost) / stats.accumulated_cost or 0
    avg_unit_cost = stats.items_bought > 0 and stats.accumulated_cost / stats.items_bought or 0
    avg_unit_earnings = stats.items_sold > 0 and stats.accumulated_earnings / stats.items_sold or 0
    stats.avg_roi_yield = avg_unit_cost > 0 and (avg_unit_earnings - avg_unit_cost) / avg_unit_cost or 0

  ndb.put_multi_async(item_stats.values())

  return newest_transaction, oldest_transaction, items


def sync_orders(character, api_orders, existing_orders):
  existing_orders = dict([(o.hash_key, o) for o in existing_orders])
  to_put = []

  for row in api_orders.orders:
    issued = datetime.fromtimestamp(row.issued)
    hash_key = hash((character.char_id,
                    row.volEntered,
                    str(row.stationID),
                    str(row.typeID),
                    issued))

    existing = existing_orders.get(hash_key, None)
    if existing:
      existing.remaining_quantity = row.volRemaining
      existing.order_state = row.orderState
      to_put.append(existing)

    else:
      order = MarketOrder(hash_key=hash_key,
                          character_key=character.key,
                          char_id=character.char_id,
                          original_quantity=row.volEntered,
                          remaining_quantity=row.volRemaining,
                          station_id=str(row.stationID),
                          type_id=str(row.typeID),
                          unit_price=row.price,
                          order_type=(row.bid and MarketOrder.BUY or MarketOrder.SELL),
                          order_state=row.orderState,
                          issued=issued)
      to_put.append(order)

  ndb.put_multi_async(to_put)

