# -*- coding: UTF-8 -*-

from maeve.api import Api
from maeve.models import Character, Account, WalletTransaction
from google.appengine.ext import ndb
from datetime import datetime
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


def index_all_characters():

  for char_future, acct_future in get_characters_and_accounts():
    characters, accounts = char_future.get_result(), acct_future.get_result()

    accounts = dict([(a.key, a) for a in accounts])
    #latest_transactions = map(get_latest_transaction, characters)
    #latest_transactions_by_char = {}
    #for kt_gen in latest_transactions:
    #  for key, transaction in kt_gen:
    #    latest_transactions_by_char[key] = transaction

    for character in characters:
      account = accounts.get(character.account_key, None)
      if account:
        index_character(character, account)#, latest_transactions_by_char.get(character.key, None))


def index_character(character, account):
  api = Api(account.api_id, account.api_vcode)
  api.authenticate()
  api_char = api.get_character(character.char_id)

  row_count = 250

  character.last_update = datetime.now()
  last_transaction_id = character.last_transaction_id

  api_wallet_transactions = api_char.WalletTransactions(rowCount=(last_transaction_id is None and 1000 or row_count))
  newest_transaction, oldest_transaction = sync_transactions(character, api_wallet_transactions, last_transaction_id)

  while last_transaction_id and oldest_transaction and oldest_transaction.transactionID > last_transaction_id:
    logging.info('Fetching another batch from id {0}'.format(oldest_transaction.transactionID))
    api_wallet_transactions = api_char.WalletTransactions(rowCount=row_count, fromID=oldest_transaction.transactionID)
    newest_transaction, oldest_transaction = sync_transactions(character, api_wallet_transactions, last_transaction_id)

  character.put_async()


def sync_transactions(character, api_wallet_transactions, last_transaction_id):
  newest_transaction, oldest_transaction = None, None
  to_put = []

  for row in api_wallet_transactions.transactions:
    if not last_transaction_id or row.transactionID > last_transaction_id:
      wt = WalletTransaction(character_key=character.key,
                             char_id=character.char_id,
                             transaction_id=row.transactionID,
                             transaction_date=datetime.fromtimestamp(row.transactionDateTime),
                             quantity=int(row.quantity),
                             type_name=row.typeName,
                             type_id=str(row.typeID),
                             unit_price=int(row.price),
                             client_id=str(row.clientID),
                             client_name=str(row.clientName),
                             transaction_type=(row.transactionType == 'sell' and WalletTransaction.SELL or WalletTransaction.BUY),
                             journal_transaction_id=str(row.journalTransactionID))

      to_put.append(wt)
    else:
      logging.info('Skipped transaction {0}'.format(row.transactionID))

    if not oldest_transaction or row.transactionID < oldest_transaction.transactionID:
      oldest_transaction = row

    if not newest_transaction or row.transactionID > newest_transaction.transactionID:
      newest_transaction = row

    character.last_transaction_id = max(character.last_transaction_id, row.transactionID)

  ndb.put_multi_async(to_put)

  return newest_transaction, oldest_transaction
