from google.appengine.api import users
from google.appengine.ext import db
import webapp2
import json
import ResolutionAction
import ResolutionInfo
from ValidUserRequestHandler import ValidUserJSONHandler
import dblayer

def performAction(UId, ri, actionTuple, param):
    oldRI = dblayer.getResolutionInfo(ri.resolutionId)
    if not oldRI.ownerId == UId:
        return None, "USER_DOESNT_OWN_RESOLUTION"
    try:
        actionTuple.actionFunc(ri, param)
    except:
        return None, "UNKNOWN_ERROR"
    return json.dumps({"Error": None, "Success": True}), None


class ActionHandler(ValidUserJSONHandler):
    def convertResolutionObject(self, rco): #why is this necessary
        ri = dblayer.getResolutionInfo(rco['id'])
        if 'spanish' in rco:
            ri.spanishResolution = rco['spanish']
        if 'english' in rco:
            ri.englishR/solution = rco['english']
        ri.comments = rco['comments']
    def postWithUser(self):
        try:
            resolutionClientObject = json.loads(self.request.body)
        except ValueError:
            self.writeRequestErrorResponse("GARBAGE_JSON")
            return
        try:
            ri = self.convertResolutionObject(resolutionClientObject)
        except:
            self.writeRequestErrorResponse("CANT_CONVERT_RESOLUTION")
            return
        actions = self.wbUser.getResolutionActions(ri.status)
        try:
            action = next(x for x in actions if x.actionID == resolutionClientObject["action"])
        except (ValueError, KeyError):
            self.writeRequestErrorResponse("NO_ACTION_SPECIFIED")
            return
        except StopIteration:
            self.writeRequestErrorResponse("USER_CANT_PERFORM_THIS_ACTION")
            return
        for verification in action.verifications:
            if not ActionVerifications.verify(verification, ri):
                self.writeRequestErrorResponse("FAILED_VERIFICATION")
                return
        try:
            actionParam = resolutionClientObject["param"]
        except KeyError:
            actionParam = None
        result, err = performAction(self.wbUser.UId, ri, action, param)
        if (err):
            self.writeRequestErrorResponse(err)
            return
        self.response.out.write(result)
        return
