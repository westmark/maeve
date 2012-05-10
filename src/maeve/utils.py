# -*- coding: UTF-8 -*-

from calendar import Calendar
from datetime import datetime, timedelta, date
from google.appengine.ext.ndb import model
import os
import re
import time

monday_calendar = Calendar(0)


def slugify(inStr):
  removelist = ["a", "an", "as", "at", "before", "but", "by", "for", "from", "is", "in", "into", "like", "of", "off", "on", "onto", "per", "since", "than", "the", "this", "that", "to", "up", "via", "with"]
  for a in removelist:
    aslug = re.sub(r'\b' + a + r'\b', '', inStr)
  aslug = re.sub('[^\w\s-]', '', aslug).strip().lower()
  aslug = re.sub('\s+', '-', aslug)
  return aslug


def is_prod_environment():
  return not os.environ.get('SERVER_SOFTWARE', '').startswith('Development')


def to_UTC(dt):
  from pytz.gae import pytz

  if dt.tzinfo:
    return dt.astimezone(pytz.utc)
  else:
    return pytz.utc.localize(dt)


def to_msTS(d):
  return int(time.mktime(d.timetuple()) * 1000000 + d.microsecond)


def to_jstime(dt):
  if dt:
    #dt = to_CET(dt) #FIXME
    return int(time.mktime(dt.timetuple()) * 1000)
  return None


def date_fmt(d, fmt='%Y-%m-%d'):
  return d.strftime(fmt)


def to_datetime(datetime_str):
  if type(datetime_str) is datetime:
    return datetime_str

  if datetime_str:
    return datetime.utcfromtimestamp(int(datetime_str))
  return None

milliseconds_ptrn = re.compile(r'^\d+$')
date_patterns = (
                 ('%Y/%m/%d', 'YYYY/MM/DD', re.compile(r'^\d{4}/[01]\d/[0123]\d$')),
                 ('%Y-%m-%d', 'YYYY-MM-DD', re.compile(r'^\d{4}-[01]\d-[0123]\d$')),
                 )


def to_date(datetime_str):
  if type(datetime_str) is date:
    return datetime_str
  dt = None
  if not datetime_str:
    return dt
  if milliseconds_ptrn.match(datetime_str):
    dt = to_datetime(datetime_str)
  else:
    for dt_ptrn, _, ptrn in date_patterns:
      if ptrn.match(datetime_str):
        dt = datetime.strptime(datetime_str, dt_ptrn)
  if dt:
    return dt.date()
    #return to_CET(dt).date() #FIXME


def convert_timezones(timezones_str_list):
  from pytz.gae import pytz

  timezones, now, zero_td = [], pytz.utc.localize(datetime.now()), timedelta()
  for timezone_str in timezones_str_list:
    tz = pytz.timezone(timezone_str)
    offset = now.astimezone(tz).utcoffset()
    if offset.days < 0:
      hours = ((zero_td - offset).seconds / 3600) * (offset.days < 0 and -1 or 1)
    else:
      hours = offset.seconds / 3600

    timezones.append((timezone_str, hours))
  return sorted(timezones, cmp=lambda a, b: a[1] == b[1] and cmp(a[0], b[0]) or cmp(a[1], b[1]))


def to_model_key(urlsafe_str_or_key):
  if isinstance(urlsafe_str_or_key, model.Key):
    return urlsafe_str_or_key
  try:
    return model.Key(urlsafe=urlsafe_str_or_key)
  except:
    return None


class IntegrityException(Exception):
  def __init__(self, message, key):
    self.message = message
    self.key = repr(key)

  def __str__(self):
    return repr(self.message) + ' Offending key: ' + self.key
