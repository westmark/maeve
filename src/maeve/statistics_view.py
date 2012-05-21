# -*- coding: UTF-8 -*-

from maeve.web import BaseHandler, profile_required
from maeve.settings import webapp2_config
from maeve.utils import is_prod_environment, GenericModelEncoder, price_fmt
from maeve.models import Character, WalletTransaction
from maeve.statistics import get_filtered_transactions
from google.appengine.ext.ndb import toplevel
from google.appengine.api import users
import webapp2
import json


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



app = webapp2.WSGIApplication([
                                (r'/stat/transactions?$', TransactionsHandler),
                              ],
                              debug=(not is_prod_environment()),
                              config=webapp2_config
                              )
