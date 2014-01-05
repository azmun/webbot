import webapp2
import logging
from google.appengine.api import users
import dblayer
import json

SUCCESS = 0
class ValidUserRequestHandler(webapp2.RequestHandler):
    def writeInvalidUser(self, msg=None):
        messageTemplate = '<html><body><p>%s</p><p><a href="%s">logout</a></p></body></html>' 
        if not msg:
            msg = "This e-mail account is not authorized to access this application."
        self.response.out.write(messageTemplate % (msg, users.create_logout_url('/')))
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
            validationCode = self.validateUser(self.wbUser)
            if validationCode != SUCCESS:
                self.writeInvalidUser(self.getValidationErrorMsg(validationCode))
                return False, None
        except dblayer.NoSuchUserError:
            self.writeInvalidUser()
            return False, None
        return True, None
    def validateUser(self, _):
        return SUCCESS
    def getValidationErrorMsg(self, validationCode):
        return "Unknown error"
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

