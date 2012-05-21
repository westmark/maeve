# -*- coding: UTF-8 -*-

import os
from maeve.utils import is_prod_environment, date_fmt, datetime_fmt

webapp2_config = {
  'webapp2_extras.jinja2': {
    'environment_args': {
    },
    'template_path': os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates')),
    'filters': {
      'date_fmt': date_fmt,
      'datetime_fmt': datetime_fmt
    },
  },
  'webapp2_extras.sessions': {
    'cookie_args': {
      'secure': is_prod_environment(),
    },
    'secret_key': '&0q^Cd]P|@:lp}%MP}Ni2sUjP+A]IcK/j3(7ta(g]|K3ESykQ5GE1NrRlx)>#;OwYG>).G?6(y4V\/>2,um\R%;7lON>0p0aRs6]3#dJ6imR%X_*|}Oz3GRe@o)QgS;V',
  },
}
