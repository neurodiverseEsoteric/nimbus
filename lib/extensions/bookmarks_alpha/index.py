#!/usr/bin/env python
###
import os
import wsgiref.handlers

from google.appengine.ext import webapp
from google.appengine.api import urlfetch
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

class MainHandler(webapp.RequestHandler):

  def get(self):
    template_values = {
        'base_url': 'http://%s/' % self.get_host_name(),
        'bookmarklet': self.get_bookmarklet_code()}
    path = os.path.join(os.path.dirname(__file__), 'index.html')
    self.response.out.write(template.render(path, template_values))

  def get_host_name(self):
    if os.environ.get('HTTP_HOST'):
      url = os.environ['HTTP_HOST']
    else:
      url = os.environ['SERVER_NAME']
    return url

  def get_bookmarklet_code(self):
    return "javascript:(function(){if(document.getElementById('__wc_display')){__wc_refresh();return};window.__wc_base='http://%s/';var d=document;var s=d.createElement('script');s.setAttribute('src',__wc_base+'s/jquery.js');s.setAttribute('type','text/javascript');d.body.appendChild(s);s=d.createElement('script');s.setAttribute('src',__wc_base+'s/wc.js');s.setAttribute('type','text/javascript');d.body.appendChild(s);})()" % (self.get_host_name())


def main():
  application = webapp.WSGIApplication([('/', MainHandler)],
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
