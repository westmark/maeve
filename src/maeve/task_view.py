# -*- coding: UTF-8 -*-

from maeve.web import BaseHandler
from maeve.settings import webapp2_config
from maeve.utils import is_prod_environment
from maeve.tasks import index_all_characters
from google.appengine.ext.ndb import toplevel
import webapp2


class TaskHandler(BaseHandler):

  @toplevel
  def get(self):
    index_all_characters()

app = webapp2.WSGIApplication([
                                (r'/_task/?$', TaskHandler),
                              ],
                              debug=(not is_prod_environment()),
                              config=webapp2_config
                              )
