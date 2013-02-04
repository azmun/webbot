import webapp2
from webapp2 import template
import dblayer
import json

def _getGeneratedValues(user):
    ret = {}
    ret["resolutions"] = dblayer.getUserConcernedResolutions(user)
    ret["committees"] = dblayer.getAllCommittees()
    return ret

class IndexHandler(webapp2.RequestHandler):
    def get(self):
        gaeUser = users.get_current_user()
        if not gaeUser:
            self.writeNotLoggedIn()
            return
        wbUser = dblayer.getWebbotUserByEmail(gaeUser.email())
        if not wbUser:
            self.writeInvalidUser()
        gvJson = json.dumps(_getGeneratedValues(wbUser))
        templateValues = {
            'dynamicGlobals': gvJson
        }
        path = os.path.join(os.path.dirname(__file__), 'resolution.html')
        self.response.out.write(template.render(path, templateValues))
        
