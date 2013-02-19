import webapp2

class ValidUserRequestHandler(webapp2.RequestHandler):
    def writeInvalidUser(self):
        self.response.out.write('<html><body><p>This e-mail account is not authorized to access this application.</p><p><a href="%s">logout</a></p></body></html>' % users.create_logout_url('/'))
    def writeNotLoggedIn(self):
        webapp2.redirect(users.create_login_url('/'))
    def userGuard(self):
        gaeUser = users.get_current_user()
        if not gaeUser:
            self.writeNotLoggedIn()
            return False
        self.wbUser = dblayer.getWebbotUserByEmail(gaeUser.email())
        if not self.wbUser:
            self.writeInvalidUser()
            return False
        return True
    def get(self):
        if self.userGuard():
            self.getWithUser()
    def post(self):
        if self.userGuard():
            self.postWithUser()

class ValidUserJSONHandler(ValidUserRequestHandler):
    def writeInvalidUser(self):
        self.writeRequestErrorResponse("INVALID_USER")
    def writeNotLoggedIn(self):
        self.writeRequestErrorResponse("NOT_LOGGED_IN")
    def writeRequestErrorResponse(self, error):
        self.out.response.write({"Error": error, "Success": False})

