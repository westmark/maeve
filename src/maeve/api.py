#-*- coding: UTF-8 -*-

import eveapi
import time

try:
  from webapp2 import cached_property as c_property
except:
  c_property = property


class Api(object):

  WALLET_TRANSACTIONS_MASK = 4194304
  MARKET_ORDERS_MASK = 4096
  MAIL_MASK = 2048

  def __init__(self, api_id, api_vcode):
    self.api_id = api_id
    self.api_vcode = api_vcode
    self.current_char_id = None

    self._access_mask = None

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

  @property
  def access_mask(self):
    if not self._access_mask:
      self._access_mask = self.auth.account.APIKeyInfo().key.accessMask
    return self._access_mask

  def can_access(self, *masks):
    mask = reduce(lambda a, b: a | b, masks, 0)
    return self.access_mask & mask == mask


def get_reftype_by_name(reftype_name):
  eve_api = eveapi.EVEAPIConnection()
  rt = eve_api.eve.RefTypes().refTypes
  rtn = rt.IndexedBy('refTypeName')
  try:
    t = rtn.Get(reftype_name)
    return t.refTypeID
  except:
    return None
