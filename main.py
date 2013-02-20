import webapp2
from google.appengine.ext.webapp.util import run_wsgi_app
import h_do_new
import h_action
import h_index
import h_new

app = webapp2.WSGIApplication(
        [('/', h_index.IndexHandler),
         ('/action', h_action.ActionHandler),
         ('/do_new', h_do_new.DoNewHandler),
         ('/new_resolution', h_new.NewHandler)],
        debug=True)

def main():
    run_wsgi_app(app)

if __name__ == '__main__':
    main()
