#from gevent.server import StreamServer

from gevent import monkey; monkey.patch_all()

from random import sample, randint
from string import ascii_letters

from gevent.pywsgi import WSGIServer
import gevent
import web

HOST = '0.0.0.0'
PORT = 8000

routes = (
  "/bounce/", "Bounce",
  "/bounce/(.*)", "Bounce",
  "/infinidom/", "InfiniDOM",
  "/flood/", "Flood",
  "/mute/", "Mute",
  "/trickle/", "Trickle",
  "/junkmail/", "Junkmail",
)

def junk_str():
  return ''.join(sample(ascii_letters, 10))

def junk_email():
  return '%s@example.net' % junk_str()

def junk_credit_card():
  return '%d %d %d %d' % tuple(randint(1000, 9999) for i in range(4))


class Flood:
  """\
  Let's see how much data this person
  wants. 
  """
  def GET(self):
    web.ctx['headers'].append(('X-Powered-By', 'rust'))
    msg = 'Y U NO LEAVE US ALONE?\r\n'*2000
    # roughly 250M/s on localhost
    yield '<!DOCTYPE html><html><head></head><body><pre>\r\n'
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
    from pprint import pprint
    web.ctx['headers'].append(('X-Powered-By', 'rust'))
    yield '<!DOCTYPE html><html><head></head><body><pre>\r\n'
    while 1:
      yield junk_str()
      yield '\r\n'
      gevent.sleep(1)


class Mute:
  """\
  Let's just wait and see what will happen
  with giving them nothing. If they have
  implemented things poorly, this will
  hold up one of their threads ad infinitum. 
  """
  def GET(self):
    web.ctx['headers'].append(('X-Powered-By', 'rust'))
    while 1:
      yield ''
      gevent.sleep(10)


class Bounce:
  """\
  Let's clog up their HTTP request queue.
  """
  def GET(self, meh=None):
    web.ctx['headers'].append(('X-Powered-By', 'rust'))
    raise web.seeother('/bounce/%s' % ''.join(sample(ascii_letters, 10)))


class Junkmail:
  """\
  Many spammers are looking for email adresses. 
  Let's see if we can clog up their system by providing
  hundreds of valid, unique & useless addresses. That
  wont stop them, but it may produce a bottleneck 
  further down their pipeline.
  """
  def GET(self):
    web.ctx['headers'].append(('X-Powered-By', 'rust'))
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
    web.ctx['headers'].append(('X-Powered-By', 'rust'))
    yield '<!DOCTYPE html><html><head></head><body>'
    while 1:
      yield '<div>' * 1000
      gevent.sleep(0.1)


if __name__ == "__main__":


  app = web.application(routes, globals()).wsgifunc()
  print 'Serving on %s:%d' % (HOST, PORT)
  WSGIServer((HOST, PORT), app).serve_forever()
