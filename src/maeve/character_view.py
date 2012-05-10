# -*- coding: UTF-8 -*-

from maeve.web import BaseHandler, profile_required
from maeve.settings import webapp2_config
from maeve.utils import is_prod_environment
from maeve.models import Account, Character
from maeve.api import get_auth, get_characters
from google.appengine.ext.ndb import toplevel
from google.appengine.api import users
import webapp2


class CharacterHandler(BaseHandler):

  def get(self, char_id):
    env = {}

    char = self.userprofile.get_char(char_id)
    if char:
      env.update(dict(character=char,
                      account=char.account))

      if char.active:
        pass

      self.render_response('character/index.html', env)
    else:
      self.session.add_flash('No character with that id found', key='top_messages')
      self.redirect('/profile')


class CharacterActivationHandler(BaseHandler):

  def post(self, char_id, action):

    char = self.userprofile.get_char(char_id)
    if char:
      active_char_ids = char.account.active_char_ids or []

      if action == 'activate':
        active_char_ids.append(char.char_id)
        self.session.add_flash('Character {0} activated!'.format(char.name), key='top_messages', level='success')

      char.account.active_char_ids = active_char_ids
      char.account.put_async()
      self.redirect('/character/{0}'.format(char.char_id))

    else:
      self.session.add_flash('No character with that id found', key='top_messages', level='warning')
      self.redirect('/profile')

app = webapp2.WSGIApplication([
                                (r'/character/(\d+)/?$', CharacterHandler),
                                (r'/character/(\d+)/(activate)/?$', CharacterActivationHandler),
                              ],
                              debug=(not is_prod_environment()),
                              config=webapp2_config
                              )
