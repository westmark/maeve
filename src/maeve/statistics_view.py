# -*- coding: UTF-8 -*-

from maeve.web import BaseHandler, character_view
from maeve.settings import webapp2_config
from maeve.utils import is_prod_environment, GenericModelEncoder, price_fmt, to_jstime
from maeve.models import WalletTransaction, ItemTypeIndex, StationIndex
from maeve.statistics import get_filtered_transactions
import webapp2
import json
import numpy


class CoreItemStatsHandler(BaseHandler):
  @character_view
  def get(self):
    env = {
      'WalletTransaction': WalletTransaction
    }
    self.render_response('character/itemanalysis.html', env)


class TransactionsHandler(BaseHandler):

  @character_view
  def get(self):
    filters = json.loads(self.request.get('filters', '{}'))
    item_index, station_index = ItemTypeIndex.query().get_async(), StationIndex.query().get_async()
    result = get_filtered_transactions(self.character, filters)

    results_as_dct = [r.to_dict() for r in result]
    item_index, station_index = item_index.get_result().items, station_index.get_result().stations

    for dct in results_as_dct:
      dct['balance_change'] = dct['unit_price'] * dct['quantity']
      if dct['transaction_type'] == WalletTransaction.BUY:
        dct['balance_change'] *= -1

      dct['balance_change_str'] = price_fmt(dct['balance_change'])
      dct['unit_price_str'] = price_fmt(dct['unit_price'])
      dct['type_name'] = item_index.get(dct['type_id'], '<Unknown item>')
      dct['station_name'] = station_index.get(dct['station_id'], '<Unknown station>')

    self.render_json(results_as_dct, cls=GenericModelEncoder)


class TransactionsMeanPriceHandler(BaseHandler):

  @character_view
  def get(self):
    try:
      type_id = self.request.get('type_id', None)
      item_index = ItemTypeIndex.query().get_async()
      quantity = int(self.request.get('quantity', 10) or 10)
      transaction_type = int(self.request.get('transaction_type', WalletTransaction.BUY))

      result = get_filtered_transactions(self.character,
                                         filters=dict(transaction_type=transaction_type,
                                                      type_id=type_id,
                                                      limit=quantity))

      oldest_date, prices, i, item_name = None, [], 0, None
      item_index = item_index.get_result().items

      for t in result:
        if not item_name:
          item_name = item_index.get(t.type_id, '<Unknown item>')
        if i >= quantity:
          break

        oldest_date = t.transaction_date
        for j in range(t.quantity):
          prices.append(t.unit_price)
          i += 1
          if i >= quantity:
            break

      self.render_json(dict(prices=prices,
                            item_name=item_name,
                            transaction_type=transaction_type,
                            transaction_type_name=(transaction_type == WalletTransaction.BUY and 'Buy' or 'Sell'),
                            oldest_date=to_jstime(oldest_date),
                            median=price_fmt(numpy.median(prices)),
                            mean=price_fmt(numpy.mean(prices))))

    except:
      import traceback
      import logging
      logging.error(traceback.format_exc())
      self.render_json(dict(error='Bad values'))


class SeachCommodityHandler(BaseHandler):

  def get(self):
    query = self.request.get('query', '')
    index = ItemTypeIndex.query().get()

    self.render_json(dict(matches=index.find(query)))

app = webapp2.WSGIApplication([
                                (r'/stat/commodity/stats/?', CoreItemStatsHandler),
                                (r'/stat/commodity/search/?$', SeachCommodityHandler),
                                (r'/stat/transactions/?$', TransactionsHandler),
                                (r'/stat/transactions/mean/?$', TransactionsMeanPriceHandler),
                              ],
                              debug=(not is_prod_environment()),
                              config=webapp2_config
                              )
