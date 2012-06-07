# -*- coding: UTF-8 -*-

from maeve.web import BaseHandler
from maeve.settings import webapp2_config
from maeve.utils import is_prod_environment
from maeve.models import Profile
from google.appengine.ext.ndb import toplevel
from google.appengine.api import users
import webapp2


class ProfileAdminHandler(BaseHandler):

  def get(self,):
    self.render_response('admin/index.html')

  def post(self):


app = webapp2.WSGIApplication([
                                (r'/admin/profile/?$', ProfileAdminHandler),
                              ],
                              debug=(not is_prod_environment()),
                              config=webapp2_config
                              )
