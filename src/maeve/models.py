# -*- coding: UTF-8 -*-

from google.appengine.ext.ndb import model
from google.appengine.api import users
from webapp2 import cached_property


class Character(model.Model):
  name = model.StringProperty(required=True)
  char_id = model.StringProperty(required=True)
  account_key = model.KeyProperty(kind='Account')

  @cached_property
  def account(self):
    return self.account_key.get()

  @property
  def active(self):
    return self.char_id in self.account.active_char_ids


class Account(model.Model):
  user = model.UserProperty(required=True)
  key_name = model.StringProperty()
  api_vcode = model.StringProperty(required=True)
  api_id = model.StringProperty(required=True)
  active_char_ids = model.StringProperty(repeated=True)
  available_char_ids = model.StringProperty(repeated=True)
  last_update = model.DateTimeProperty()

  @classmethod
  def by_user(cls, user=None):
    user = user or users.get_current_user()
    return Account.query().filter(Account.user == user)


class Profile(model.Model):
  user = model.UserProperty()
  characters = model.LocalStructuredProperty(Character, repeated=True)

  token = model.StringProperty()

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
