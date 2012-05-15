# -*- coding: UTF-8 -*-

from google.appengine.ext.ndb import model
from google.appengine.api import users
from webapp2 import cached_property


class Character(model.Model):
  user = model.UserProperty(required=True)
  name = model.StringProperty(required=True)
  char_id = model.StringProperty(required=True)
  account_key = model.KeyProperty(kind='Account')
  #last_transaction_key = model.KeyProperty(kind='WalletTransaction')
  last_transaction_id = model.IntegerProperty()
  last_update = model.DateTimeProperty()
  active = model.BooleanProperty(default=False)

  @cached_property
  def account(self):
    return self.account_key.get()

  @classmethod
  def by_char_id(cls, char_id):
    return Character.query().filter(Character.char_id == char_id).get()

  @classmethod
  def by_user(cls, user=None):
    user = user or users.get_current_user()
    return Character.query().filter(Character.user == user)


class Account(model.Model):
  user = model.UserProperty(required=True)
  key_name = model.StringProperty()
  api_vcode = model.StringProperty(required=True)
  api_id = model.StringProperty(required=True)

  @classmethod
  def by_user(cls, user=None):
    user = user or users.get_current_user()
    return Account.query().filter(Account.user == user)

  @cached_property
  def characters(self):
    return list(Character.query().filter(Character.account_key == self.key))

  @property
  def active_characters(self):
    return [c for c in self.characters if c.active]

  @property
  def inactive_characters(self):
    return [c for c in self.characters if not c.active]


class Profile(model.Model):
  user = model.UserProperty()
  token = model.StringProperty()

  @cached_property
  def characters(self):
    return list(Character.query().filter(Character.user == self.user))

  def get_char(self, char_id):
    for c in self.characters:
      if c.char_id == char_id:
        return c

  @property
  def char_map(self):
    return dict([(c.char_id, c) for c in self.characters])

  @classmethod
  def by_user(cls, user=None):
    user = user or users.get_current_user()
    return Profile.query().filter(Profile.user == user).get()

  @classmethod
  def by_token(cls, token):
    return Profile.query().filter(Profile.token == token).get()

  @classmethod
  def create(cls, user):
    profile = Profile(user=user)
    profile.put()
    return profile


class WalletTransaction(model.Model):

  BUY = 1
  SELL = 2

  character_key = model.KeyProperty(kind='Character', required=True)
  char_id = model.StringProperty('cid', required=True)
  transaction_id = model.IntegerProperty('ti', required=True)
  transaction_date = model.DateTimeProperty('td', required=True)
  quantity = model.IntegerProperty('q', required=True, indexed=False)
  type_name = model.StringProperty('tn', required=True)
  type_id = model.StringProperty('tyi', required=True)
  unit_price = model.FloatProperty('up', required=True, indexed=False)
  client_id = model.StringProperty('cli', required=True, indexed=False)
  client_name = model.StringProperty('cln', required=True, indexed=False)
  transaction_type = model.IntegerProperty('tt', required=True, choices=[BUY, SELL])
  journal_transaction_id = model.StringProperty('jti', indexed=False)


class ItemTypeIndex(model.Model):

  items = model.JsonProperty(default={})

  @classmethod
  def get(cls, item_id):
    idx = ItemTypeIndex.query().get()
    return idx.items or {}
