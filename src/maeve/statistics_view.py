# -*- coding: UTF-8 -*-

from maeve.web import BaseHandler, profile_required
from maeve.settings import webapp2_config
from maeve.utils import is_prod_environment
from maeve.models import Character
from google.appengine.ext.ndb import toplevel
from google.appengine.api import users
import webapp2


class StatisticsHandler(BaseHandler):

  def get(self):



app = webapp2.WSGIApplication([
                                (r'/stat/?$', StatisticsHandler),
                              ],
                              debug=(not is_prod_environment()),
                              config=webapp2_config
                              )
