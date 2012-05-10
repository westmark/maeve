#-*- coding: UTF-8 -*-

import eveapi
import time


def get_auth(api_id, api_vcode):
  api = eveapi.EVEAPIConnection()
  return api.auth(keyID=api_id, vCode=api_vcode)


def get_characters(auth):
  return auth.account.Characters().characters


def get_character(auth, char_id):
  return auth.character(char_id)


def get_reftype_by_name(auth, reftype_name):
  rt = auth.eve.RefTypes().refTypes
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
