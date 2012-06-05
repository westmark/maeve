# -*- coding: UTF-8 -*-

from maeve.models import Character, WalletTransaction
from maeve.utils import price_fmt
from datetime import datetime
import logging


def extend_transactions_query_result(result):
  results_as_dct = [r.to_dict() for r in result]
  for dct in results_as_dct:
    dct['balance_change'] = dct['unit_price'] * dct['quantity']
    if dct['transaction_type'] == WalletTransaction.BUY:
      dct['balance_change'] *= -1

    dct['balance_change_str'] = price_fmt(dct['balance_change'])
    dct['unit_price_str'] = price_fmt(dct['unit_price'])


def get_filtered_transactions(character, filters):
  transaction_type = filters.get('transaction_type', None)
  if 'limit' in filters:
    limit = filters['limit']
  else:
    if transaction_type:
      limit = 40
    else:
      limit = 20

  query = WalletTransaction.query(WalletTransaction.character_key == character.key)

  if transaction_type:
    if type(transaction_type) in (str, unicode):
      if transaction_type.lower() == 'sell':
        transaction_type = WalletTransaction.SELL
      elif transaction_type.lower() == 'buy':
        transaction_type = WalletTransaction.BUY

    query = query.filter(WalletTransaction.transaction_type == int(transaction_type))

  if 'type_id' in filters:
    query = query.filter(WalletTransaction.type_id == filters['type_id'])

  if 'older' in filters:
    query = query.filter(WalletTransaction.transaction_date < datetime.fromtimestamp(int(filters['older'])))
  elif 'newer' in filters:
    query = query.filter(WalletTransaction.transaction_date > datetime.fromtimestamp(int(filters['newer'])))

  query = query.order(-WalletTransaction.transaction_date)
  return query.fetch(limit)
