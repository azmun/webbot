import webapp2
from google.appengine.ext.webapp.util import run_wsgi_app
import h_do_new
import h_action
import h_index
import h_new
import h_new_topic
import h_do_new_topic
import h_generate
import h_admin_gateway

app = webapp2.WSGIApplication(
        [('/', h_index.IndexHandler),
         ('/admin', h_admin_gateway.AdminGatewayHandler),
         ('/action', h_action.ActionHandler),
         ('/do_new', h_do_new.DoNewHandler),
         ('/new_resolution', h_new.NewHandler),
         ('/new_topic', h_new_topic.NewTopicHandler),
         ('/do_new_topic', h_do_new_topic.DoNewTopicHandler),
         ('/generate', h_generate.GenerateDocumentHandler)],
        debug=True)

def main():
    run_wsgi_app(app)

if __name__ == '__main__':
    main()
