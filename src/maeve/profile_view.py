# -*- coding: UTF-8 -*-

from maeve.web import BaseHandler, profile_required
from maeve.settings import webapp2_config
from maeve.utils import is_prod_environment
from maeve.models import Account, Character
from maeve.api import get_auth, get_characters
from google.appengine.ext.ndb import toplevel
from google.appengine.api import users
import webapp2


class ProfileHandler(BaseHandler):

  @profile_required
  def get(self):
    env = dict()
    flash_env = self.session.get_flashes(key='env_flash')
    if flash_env:
      for e, _ in flash_env:
        env.update(e)

    active_chars, inactive_chars = [], []
    char_map = self.userprofile.char_map

    for account in Account.by_user():
      for char_id in account.available_char_ids:
        if char_id in account.active_char_ids:
          active_chars.append((char_map.get(char_id), account.key.urlsafe()))
        else:
          inactive_chars.append((char_map.get(char_id), account.key.urlsafe()))

    env.update(dict(active_chars=active_chars,
                    inactive_chars=inactive_chars))

    self.render_response('profile/index.html', env)


class ApiHandler(BaseHandler):

  @toplevel
  @profile_required
  def post(self):
    api_vcode = self.request.POST.get('api_vcode', None)
    api_id = self.request.POST.get('api_id', None)

    if not (api_id and api_vcode) or not(len(api_id) == 6 and len(api_vcode) == 64):
      env = dict(values=dict(api_id=api_id, api_vcode=api_vcode),
                 errors=dict(api_id=(not api_id or len(api_id) != 6), api_vcode=(not api_vcode or len(api_vcode) != 64)))

      self.session.add_flash(env, key='env_flash')

    else:
      if Account.query().filter(Account.api_id == api_id).count():
        self.session.add_flash('This API key has already been added to this profile', key='error_messages')
      else:
        auth = get_auth(api_id, api_vcode)
        if auth:
          api_characters = get_characters(auth)
          accounts_chars = []

          for api_char in api_characters:
            if not filter(lambda c: api_char.charactedID == c.char_id, self.userprofile.characters):
              accounts_chars.append(Character(name=api_char.name,
                                              char_id=str(api_char.characterID)))

          account = Account(
                            user=users.get_current_user(),
                            api_vcode=api_vcode,
                            api_id=api_id,
                            key_name=self.request.POST.get('name', None),
                            available_char_ids=[c.char_id for c in accounts_chars],
                            )
          account.put()

          for char in accounts_chars:
            char.account_key = account.key

          self.userprofile.characters = (self.userprofile.characters or []) + accounts_chars
          self.userprofile.put_async()

          self.session.add_flash('Key added successfully', key='messages')

    self.redirect('/profile')

app = webapp2.WSGIApplication([
                                (r'/profile/?$', ProfileHandler),
                                (r'/profile/api/?$', ApiHandler),
                              ],
                              debug=(not is_prod_environment()),
                              config=webapp2_config
                              )
