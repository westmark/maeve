# -*- coding: UTF-8 -*-

from maeve.utils import is_prod_environment
from webapp2 import RequestHandler, cached_property
from webapp2_extras import jinja2, sessions, sessions_ndb
from google.appengine.api import users
from maeve.models import Profile
import logging
import simplejson as json

JINJA2_KEY = 'maeve.jinja2.instance.1'


class BaseHandler(RequestHandler):

  @cached_property
  def jinja2(self):
    return jinja2.get_jinja2(key=JINJA2_KEY,
                             app=self.app)

  @cached_property
  def session(self):
    session = self.session_store.get_session(name='db_session', factory=sessions_ndb.DatastoreSessionFactory)
    return session

  @cached_property
  def userprofile(self):
    if users.get_current_user():
      return Profile.by_user(users.get_current_user())

  def redirect(self, uri, *args, **kwargs):
    if self.is_ajax():
      self.response.headers['x-redirect'] = uri
    else:
      super(BaseHandler, self).redirect(uri, *args, **kwargs)

  def render_template(self, _template, context={}):
    context.update(dict(
                        top_messages=self.session.get_flashes(key='top_messages'),
                        messages=self.session.get_flashes(key='messages'),
                        error_messages=self.session.get_flashes(key='error_messages'),
                        profile=self.userprofile,
                        debug=(not is_prod_environment())
                        ))

    return self.jinja2.render_template(_template, **context)

  def render_response(self, _template, context={}):
    self.response.write(self.render_template(_template, context))

  def render_json(self, json_data=None, encoder=None, redirect=None):
    self.response.headers['Content-Type'] = 'application/json'
    if json_data:
      if encoder:
        self.response.out.write(json.dumps(json_data, default=encoder))
      else:
        self.response.out.write(json.dumps(json_data))

    if redirect:
      self.response.headers['x-redirect'] = str(redirect)

  def render_javascript(self, js_data):
    self.response.headers['Content-Type'] = 'application/javascript'
    self.response.out.write(js_data)

  def decode_json(self, json_data):
    dict_ = {}
    for k, v in json.loads(json_data).iteritems():
      v = v or None
      if isinstance(k, unicode):
        k = str(k)
      dict_[k] = v
    return dict_

  def decode_values(self):
    return self.decode_json(self.request.get('values'))

  def is_ajax(self):
    return 'XMLHttpRequest' == self.request.headers.get('X-Requested-With', False)

  def dispatch(self):
    self.session_store = sessions.get_store(request=self.request)

    try:
      RequestHandler.dispatch(self)
    except:
      import traceback
      logging.error(traceback.format_exc())
      d = dict(stacktrace=traceback.format_exc(),
               req=self.request)
      self.render_response('error/general.html', d)
    finally:
      self.session_store.save_sessions(self.response)

      if 'msie' in self.request.headers['User-Agent'].lower():
        self.response.headers['X-UA-Compatible'] = 'IE=edge,chrome=1'


def profile_required(fn):
  def wrapped(self, *args, **kwargs):
    if users.get_current_user() and self.userprofile is None:
      if users.is_current_user_admin():
        self.userprofile = Profile.create(user=users.get_current_user())
      else:
        redirect_to = '/user/profile/create?next={0}'.format(self.request.path + (self.request.query and ('?' + self.request.query) or ''))
        return self.redirect(redirect_to)

    return fn(self, *args, **kwargs)
  return wrapped
