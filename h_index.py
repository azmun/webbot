import webapp2
from webapp2 import template
import dblayer
import json
from ActionVerification import ActionVerifications
from ActionDialogs import ActionDialogs
from ValidUserRequestHandler import ValidUserRequestHandler
import Enums

def _getGeneratedValues(user):
    ret = {}
    ret["resolutions"] = dblayer.getUserConcernedResolutions(user)
    for res in ret["resolutions"]:
        res.actions = user.getResolutionActions(res.status)
    ret["committees"] = dblayer.getAllCommittees()
    ret["sortOrder"] = user.getConcernedResolutionsOrder()
    res["englishRPs"] = dblayer.getEnglishRPs()
    res["spanishRPs"] = dblayer.getSpanishRPs()
    ret["_verifications"] = {t[0]: t[1] for t in ActionVerifications}
    ret["_actionDialogs"] = {t[0]: t[1] for t in ActionDialogs}
    return ret

_newButton = r"""<input type="button" value="New resolution" onclick="newResolution(%s)" name="newResolution" />"""

def _getNewButton(committee):
    return _newButton % committee

class IndexHandler(ValidUserRequestHandler):
    def getWithUser(self):
        gvJson = json.dumps(_getGeneratedValues(self.wbUser))
        enumsJson = json.dumps(Enums.All)
        nic = ''
        committee = self.wbUser.canCreateResolutionIn()
        if committee != None
            nic = _getNewButton(committee)
        templateValues = {
            'dynamicGlobals': gvJson,
            'enumValues': enumsJson
            'newIfCan': nic
        }
        path = os.path.join(os.path.dirname(__file__), 'resolution.html')
        self.response.out.write(template.render(path, templateValues))
    
