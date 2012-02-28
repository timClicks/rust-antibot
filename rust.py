# RUST: corroding misbehaving web bots

# Copyright 2011, 2012 Tim McNamara

# This file is part of RUST.

# RUST is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# RUST is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.


from gevent import monkey; monkey.patch_all()

from random import SystemRandom, choice, sample, randint, random
from string import ascii_letters
from uuid import uuid4

from gevent.pywsgi import WSGIServer
import gevent
import web

HOST = '0.0.0.0'
PORT = 8000

routes = (
  "/bounce/", "Bounce",
  "/bounce/(.*)", "Bounce",
  "/infinidom/", "InfiniDOM",
  "/linkfury/", "LinkFury",
  "/linkfury/(.*)", "LinkFury",
  "/flood/", "Flood",
  "/mongrel/", "MongrelDOM",
  "/mute/", "Mute",
  "/trickle/", "Trickle",
  "/junkmail/", "Junkmail",
)

def junk_str():
  return uuid4().hex

def junk_email():
  return '%s@example.net' % junk_str()

def junk_credit_card():
  return '%d %d %d %d' % tuple(randint(1000, 9999) for i in range(4))

elems = (
  'div', 'p', 'span', 'h1', 'h2', 'ol', 'li',
  'ruby', 'marquee', 'blink', 'pre', 'html',
  'body', 'head'
)

def chunk(msg):
  return '%s\r\n' % msg

class Flood:
  """\
  Let's see how much data this person
  wants. 
  """
  def GET(self):
    web.header('Content-Type', 'text/html')
    web.header('X-Powered-By', 'rust')
    msg = 'Y U NO LEAVE US ALONE?\r\n'*2000
    yield '<!DOCTYPE html><html><head></head><body><pre>'
    while 1:
      yield msg
      gevent.sleep(0)


class Trickle:
  """\
  We want to look like we're sending real 
  data. Let's see how long the pest will
  hang around waiting.
  """
  def GET(self):
    web.header('Content-Type', 'text/html')
    web.header('X-Powered-By', 'rust')
    yield '<!DOCTYPE html><html><head></head><body><pre>'
    while 1:
      yield junk_str()
      gevent.sleep(1)


class Mute:
  """\
  Let's just wait and see what will happen
  with giving them nothing. If they have
  implemented things poorly, this will
  hold up one of their threads ad infinitum. 
  """
  def GET(self):
    web.header('Content-Type', 'text/html')
    web.header('X-Powered-By', 'rust')
    while 1:
      yield ''
      gevent.sleep(10)


class Bounce:
  """\
  Let's clog up their HTTP request queue.
  """
  def GET(self, meh=None):
    web.header('X-Powered-By', 'rust')
    raise web.seeother('/bounce/%s' % junk_str())


class Junkmail:
  """\
  Many spammers are looking for email adresses. 
  Let's see if we can clog up their system by providing
  hundreds of valid, unique & useless addresses. That
  wont stop them, but it may produce a bottleneck 
  further down their pipeline.
  """
  def GET(self):
    web.header('Content-Type','text/html')
    web.header('X-Powered-By', 'rust')
    yield '<html><head></head><body><ol>'
    while 1:
      yield '<li>%s</li>' % junk_email()
      gevent.sleep(0.1)


class InfiniDOM:
  """\
  It's likely that a XML DOM parser will be used
  to interpret the response. DOM parsers generally
  load the whole document into memory. Let's take 
  advantage of that.
  """
  def GET(self):
    web.header('Content-Type', 'text/html')
    web.header('X-Powered-By', 'rust')
    dom = '<div>' * 1000
    yield '<!DOCTYPE html><html><head></head><body>'
    while 1:
      yield dom
      gevent.sleep(0.1)


class MongrelDOM:
  elements = (
      lambda: '<%s' % choice(elems),
      lambda: '</%s>' % choice(elems),
      junk_str,
      junk_email,
      junk_credit_card,
      lambda: '/>',
      lambda: '<',
      lambda: '<%s class= >' % choice(elems), #opps, malformed attr
      lambda: '<>',
  )

  def GET(self):
    web.header('Content-Type', 'text/html')
    web.header('X-Powered-By', 'rust')

    yield '<!DOCTYPE html>'
    while 1:
      mess = ''.join(e() for e in (choice(self.elements) for i in range(10)))
      yield mess
      gevent.sleep(1)


class LinkFury:
  """ 
  How about giving people n^10 links that they need to crawl?
  """
  path = "/linkfury/"
  def GET(self, meh=None):
    web.header('X-Powered-By', 'rust')
    web.header('Content-Type', 'text/html')
    yield '<!DOCTYPE html>'
    for i in range(10):
      s = junk_str()
      yield '<a href="%s%s">%s</a>' % (self.path, s, s)
      gevent.sleep(0.4)

if __name__ == "__main__":
  app = web.application(routes, globals()).wsgifunc()
  print 'Serving on %s:%d' % (HOST, PORT)
  WSGIServer((HOST, PORT), app).serve_forever()
