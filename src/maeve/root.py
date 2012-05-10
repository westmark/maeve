# -*- coding: UTF-8 -*-

from maeve.web import BaseHandler
from maeve.settings import webapp2_config
from maeve.utils import is_prod_environment
import webapp2


class RootHandler(BaseHandler):
  def get(self):
    self.render_response('index.html')


class GeneralErrorHandler(BaseHandler):
  def get(self):
    import traceback
    if not is_prod_environment():
      self.render_response('error/general.html', dict(stacktrace=traceback.format_exc()))

app = webapp2.WSGIApplication([
                                (r'/error/general/?$', GeneralErrorHandler),
                                (r'/?', RootHandler),
                              ],
                              debug=(not is_prod_environment()),
                              config=webapp2_config
                              )
