#-*- coding: UTF-8 -*-

import eveapi
import time

try:
  from webapp2 import cached_property as c_property
except:
  c_property = property


class Api(object):

  def __init__(self, api_id, api_vcode):
    self.api_id = api_id
    self.api_vcode = api_vcode
    self.current_char_id = None

  def authenticate(self):
    eve_api = eveapi.EVEAPIConnection()
    self.auth = eve_api.auth(keyID=self.api_id, vCode=self.api_vcode)
    return self

  def is_authenticated(self):
    return bool(self.auth)

  @c_property
  def characters(self):
    return self.auth.account.Characters().characters

  def get_character(self, char_id):
    return self.auth.character(char_id)

  def set_char(self, char_id):
    self.current_char_id = char_id

  def clear_char(self):
    self.current_char_id = None



def get_reftype_by_name(reftype_name):
  eve_api = eveapi.EVEAPIConnection()
  rt = eve_api.eve.RefTypes().refTypes
  rtn = rt.IndexedBy('refTypeName')
  try:
    t = rtn.Get(reftype_name)
    return t.refTypeID
  except:
    return None


def get_buy_transactions_for(auth, char, commdity_name):
  wallet = char.WalletTransactions()
  #print dir(wallet.transactions.GroupedBy('transactionType'))
  #print wallet.transactions.GroupedBy('transactionType')._cols
  #print wallet.transactions.GroupedBy('transactionType').keys()

  sold_tx = wallet.transactions.GroupedBy('transactionType')['buy']
  for row in sold_tx:#.GroupedBy('typeName'):
    print row.typeName

  return
  entries_by_type = wallet.transactions.GroupedBy('transactionType')
  market_transactions = entries_by_type[get_reftype_by_name(auth, 'Market Transaction')]
  for t_date in market_transactions.Select('date'):
    print time.asctime(time.gmtime(t_date))


def get_sell_orders(char_id, auth):
  pass
