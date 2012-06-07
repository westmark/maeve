# -*- coding: UTF-8 -*-

from maeve.web import BaseHandler
from maeve.settings import webapp2_config
from maeve.utils import is_prod_environment
from maeve.tasks import index_all_characters, index_character, update_index
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
      items, stations = index_character(character, account)
      if items:
        taskqueue.add(url='/_task/index',
                      params={
                        'items': json.dumps(items),
                        'stations': json.dumps(stations)
                      },
                      queue_name='index-update')


class IndexTaskHandler(BaseHandler):

  @toplevel
  def get(self):
    self.post()

  @toplevel
  def post(self):
    new_items = json.loads(self.request.get('items', '{}'))
    new_stations = json.loads(self.request.get('stations', '{}'))
    update_index(new_items, new_stations)


app = webapp2.WSGIApplication([
                                (r'/_cron/?$', CronHandler),
                                (r'/_task/sync/?$', SyncTaskHandler),
                                (r'/_task/index/?$', IndexTaskHandler),
                              ],
                              debug=(not is_prod_environment()),
                              config=webapp2_config
                              )
