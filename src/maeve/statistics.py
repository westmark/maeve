# -*- coding: UTF-8 -*-

from maeve.web import BaseHandler, profile_required
from maeve.settings import webapp2_config
from maeve.utils import is_prod_environment
from maeve.models import Character, WalletTransaction
from google.appengine.ext.ndb import toplevel
from google.appengine.api import users
from datetime import datetime


def get_filtered_transactions(character, filters):
  transaction_type = filters.get('type', None)
  if 'limit' in filters:
    limit = filters['limit']
  else:
    if transaction_type:
      limit = 40
    else:
      limit = 20

  query = WalletTransaction.query(WalletTransaction.character_key == character.key)

  if transaction_type:
    query = query.filter(WalletTransaction.transaction_type == int(transaction_type))

  if 'type_id' in filters:
    query = query.filter(WalletTransaction.type_id == filters['type_id'])

  if 'older' in filters:
    query = query.filter(WalletTransaction.transaction_date < datetime.fromtimestamp(int(filters['older'])))
  elif 'newer' in filters:
    query = query.filter(WalletTransaction.transaction_date > datetime.fromtimestamp(int(filters['newer'])))

  query = query.order(-WalletTransaction.transaction_date)
  return query.fetch(limit)
