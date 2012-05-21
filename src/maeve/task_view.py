# -*- coding: UTF-8 -*-

from maeve.web import BaseHandler
from maeve.settings import webapp2_config
from maeve.utils import is_prod_environment
from maeve.tasks import index_all_characters, index_character, update_item_index
from maeve.models import Character, Account
from google.appengine.ext.ndb import toplevel, model
from google.appengine.api import taskqueue
import json
import webapp2


class CronHandler(BaseHandler):

  @toplevel
  def get(self):
    index_all_characters()


class SyncTaskHandler(BaseHandler):

  @toplevel
  def get(self):
    self.post()

  @toplevel
  def post(self):
    char_key = self.request.get('char')
    character = model.Key(urlsafe=char_key).get()
    if character and character.active:
      account = character.account_key.get()
      items = index_character(character, account)
      taskqueue.add(url='/_task/index',
                    params={'values': json.dumps(items)},
                    queue_name='index-update')


class IndexTaskHandler(BaseHandler):

  @toplevel
  def get(self):
    self.post()

  @toplevel
  def post(self):
    new_values = json.loads(self.request.get('values', '{}'))
    update_item_index(new_values)


app = webapp2.WSGIApplication([
                                (r'/_cron/?$', CronHandler),
                                (r'/_task/sync/?$', SyncTaskHandler),
                                (r'/_task/index/?$', IndexTaskHandler),
                              ],
                              debug=(not is_prod_environment()),
                              config=webapp2_config
                              )
