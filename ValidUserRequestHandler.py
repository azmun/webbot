import webapp2
import logging
from google.appengine.api import users
import dblayer
import json

class ValidUserRequestHandler(webapp2.RequestHandler):
    def writeInvalidUser(self):
        self.response.out.write('<html><body><p>This e-mail account is not authorized to access this application.</p><p><a href="%s">logout</a></p></body></html>' % users.create_logout_url('/'))
    def writeNotLoggedIn(self):
        loginURL = users.create_login_url('/')
        logging.info("User not logged in, redirecting to: %s" % loginURL)
        return webapp2.redirect(loginURL)
    def writeError(self, msg):
        self.response.out.write('<html><head><title>Error page</title></head><body><p><span style="color: red; font-weight: bold">ERROR:</span>%s</p><p>Please inform Conference Services of this error.</p></body></html>' % msg)
    def userGuard(self):
        gaeUser = users.get_current_user()
        if not gaeUser:
            resp = self.writeNotLoggedIn()
            return False, resp
        try:
            self.wbUser = dblayer.getWebbotUserByEmail(gaeUser.email())
        except dblayer.NoSuchUserError:
            self.writeInvalidUser()
            return False, None
        return True, None
    def get(self):
        success, resp = self.userGuard()
        if success:
            self.getWithUser()
        elif resp:
            return resp
    def post(self):
        if self.userGuard():
            self.postWithUser()

class ValidUserJSONHandler(ValidUserRequestHandler):
    def writeInvalidUser(self):
        self.writeRequestErrorResponse("INVALID_USER")
    def writeNotLoggedIn(self):
        self.writeRequestErrorResponse("NOT_LOGGED_IN")
    def writeRequestErrorResponse(self, error):
        self.response.out.write(json.dumps({"Error": error, "Success": False}))

