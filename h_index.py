import webapp2
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.api import channel
import dblayer
import json
from ActionVerifications import ActionVerifications
from ActionDialogs import ActionDialogs
from ValidUserRequestHandler import ValidUserRequestHandler
from ResolutionActions import getSerializableVersion
import Enums
import os
import pdb

def _getGeneratedValues(user):
    ret = {}
    ret["resolutions"] = dblayer.getUserResolutions(user)
    ret["resolutionActions"] = {}
    for res in ret["resolutions"]:
        ret["resolutionActions"][res["resolutionId"]] = [getSerializableVersion(ra) for ra in user.getResolutionActions(res["status"])]
    ret["committees"] = dblayer.getAllCommittees()
    ret["sortOrder"] = user.getConcernedResolutionsOrder()
    ret["englishRPs"] = [u.__dict__ for u in dblayer.getEnglishRPs()]
    ret["spanishRPs"] = [u.__dict__ for u in dblayer.getSpanishRPs()]
    ret["_verifications"] = {t["verificationID"]: t["js"] for t in ActionVerifications}
    ret["_actionDialogs"] = {t["dialogID"]: t["js"] for t in ActionDialogs}
    return ret

_newButton = r"""<input type="button" value="New resolution" onclick="newResolution(%s)" name="newResolution" />"""
_newTopicButton = r"""<input type="button" value="New topic" onclick="newTopic(%s)" name="newTopic" />"""

def _getNewButton(committee):
    return _newButton % committee

def _getNewTopicButton(committee):
    return _newTopicButton % committee

class IndexHandler(ValidUserRequestHandler):
    def getWithUser(self):
        gvJson = json.dumps(_getGeneratedValues(self.wbUser))
        enumsJson = json.dumps(Enums.All)
        reverseEnumsJson = json.dumps(Enums.Reverse)
        nic = ''
        committee = self.wbUser.canCreateResolutionIn()
        if committee != None:
            nic = _getNewButton(committee)
        ntic = ''
        if self.wbUser.canCreateTopics():
            ntic = _getNewTopicButton(committee)
        token = channel.create_channel("%d" % self.wbUser._uId)
        templateValues = {
            'token': token,
            'dynamicGlobals': gvJson,
            'enumValues': enumsJson,
            'reverseEnumValues': reverseEnumsJson,
            'newIfCan': nic,
            'newTopicIfCan': ntic,
            'logout': users.create_logout_url('/')
        }
        path = os.path.join(os.path.dirname(__file__), 'resolution.html')
        self.response.out.write(template.render(path, templateValues))
    
