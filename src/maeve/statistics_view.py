# -*- coding: UTF-8 -*-

from maeve.web import BaseHandler, profile_required
from maeve.settings import webapp2_config
from maeve.utils import is_prod_environment, GenericModelEncoder, price_fmt, to_jstime
from maeve.models import Character, WalletTransaction, ItemTypeIndex
from maeve.statistics import get_filtered_transactions, extend_transactions_query_result
from google.appengine.ext.ndb import toplevel
from google.appengine.api import users
import webapp2
import json
import numpy


class TransactionsHandler(BaseHandler):

  def get(self):
    char_id = self.request.get('char', None)
    filters = json.loads(self.request.get('filters', '{}'))
    result = get_filtered_transactions(Character.by_char_id(char_id), filters)

    results_as_dct = [r.to_dict() for r in result]
    for dct in results_as_dct:
      dct['balance_change'] = dct['unit_price'] * dct['quantity']
      if dct['transaction_type'] == WalletTransaction.BUY:
        dct['balance_change'] *= -1

      dct['balance_change_str'] = price_fmt(dct['balance_change'])
      dct['unit_price_str'] = price_fmt(dct['unit_price'])

    self.render_json(results_as_dct, cls=GenericModelEncoder)


class TransactionsAverageHandler(BaseHandler):

  def get(self):
    try:
      char_id = self.request.get('char', None)
      type_id = self.request.get('type_id', None)
      quantity = int(self.request.get('quantity', 10))
      transaction_type = int(self.request.get('transaction_type', WalletTransaction.BUY))

      result = get_filtered_transactions(Character.by_char_id(char_id),
                                         filters=dict(transaction_type=transaction_type,
                                                      type_id=type_id,
                                                      limit=quantity))

      oldest_date, prices, i = None, [], 0
      for t in result:
        if i > quantity:
          break

        oldest_date = t.transaction_date
        for j in range(t.quantity):
          prices.append(t.unit_price)
          i += 1
          if i > quantity:
            break

      self.render_json(dict(prices=prices,
                            oldest_date=to_jstime(oldest_date),
                            median=numpy.median(prices),
                            mean=numpy.mean(prices)))

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
                                (r'/stat/commodity/search/?$', SeachCommodityHandler),
                                (r'/stat/transactions/?$', TransactionsHandler),
                                (r'/stat/transactions/average/?$', TransactionsAverageHandler),
                              ],
                              debug=(not is_prod_environment()),
                              config=webapp2_config
                              )
