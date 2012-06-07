# -*- coding: UTF-8 -*-

from maeve.web import BaseHandler, profile_required, character_view
from maeve.settings import webapp2_config
from maeve.utils import is_prod_environment
from maeve.models import Account, Character, WalletTransaction
from google.appengine.ext.ndb import toplevel
from google.appengine.api import users
import webapp2


class CharacterHandler(BaseHandler):

  @character_view
  def get(self):
    env = {}

    char = self.character

    env.update(dict(character=char,
                    account=char.account,
                    current='dashboard'))

    if char.active:
      pass

    self.render_response('character/index.html', env)


class CharacterActivationHandler(BaseHandler):

  @character_view
  def post(self, action):

    char = self.character
    if char:

      if action == 'activate':
        char.active = True
        self.session.add_flash('Character {0} activated!'.format(char.name), key='top_messages', level='success')

      char.put_async()
      self.redirect('/character?char={0}'.format(char.char_id))

    else:
      self.session.add_flash('No character with that id found', key='top_messages', level='warning')
      self.redirect('/profile')


class CharacterTransactionsHandler(BaseHandler):

  @character_view
  def get(self):
    env = {}
    env.update(dict(character=self.character,
                    account=self.character.account,
                    current='transactions'))

    if self.character.active:
      pass

      self.render_response('character/transactions.html', env)


class CharacterItemAnalysisHandler(BaseHandler):

  @character_view
  def get(self):
    env = {}
    env.update(dict(character=self.character,
                    account=self.character.account,
                    current='analysis',
                    WalletTransaction=WalletTransaction))

    if self.character.active:
      pass

      self.render_response('character/analysis.html', env)


app = webapp2.WSGIApplication([
                                (r'/character/?$', CharacterHandler),
                                (r'/character/(activate)/?$', CharacterActivationHandler),
                                (r'/character/transactions/?$', CharacterTransactionsHandler),
                                (r'/character/analysis/?$', CharacterItemAnalysisHandler),
                              ],
                              debug=(not is_prod_environment()),
                              config=webapp2_config
                              )
