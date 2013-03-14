from google.appengine.api import users
from google.appengine.ext import db
import webapp2
import json
import ResolutionActions
import ResolutionInfo
import ActionVerifications
import traceback
import logging
from ValidUserRequestHandler import ValidUserJSONHandler
import dblayer
import pdb

def performAction(UId, ri, actionTuple, param):
    oldRI = dblayer.getResolutionInfo(ri['resolutionId'])
    if not oldRI['ownerId'] == UId:
        return None, "USER_DOESNT_OWN_RESOLUTION"
    try:
        actionTuple.actionFunc(ri, param)
    except:
        logging.error(traceback.print_exc())
        return None, "UNKNOWN_ERROR"
    return json.dumps({"Error": None, "Success": True}), None


class ActionHandler(ValidUserJSONHandler):
    def convertResolutionObject(self, rco): #why is this necessary? To make sure they didn't fuck with the constants.
        ri = dblayer.getResolutionInfo(rco['id'])
        if 'spanishResolution' in rco:
            ri['spanishResolution'] = rco['spanishResolution']
        if 'englishResolution' in rco:
            ri['englishResolution'] = rco['englishResolution']
        ri['comments'] = rco['comments']
        ri['sponsors'] = rco['sponsors']
        return ri
    def postWithUser(self):
        try:
            resolutionClientObject = json.loads(self.request.body)
        except ValueError:
            self.writeRequestErrorResponse("GARBAGE_JSON")
            return
        try:
            ri = self.convertResolutionObject(resolutionClientObject)
        except:
            logging.error(traceback.format_exc())
            self.writeRequestErrorResponse("CANT_CONVERT_RESOLUTION")
            return
        actions = self.wbUser.getResolutionActions(ri['status'])
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
        result, err = performAction(self.wbUser.getUId(), ri, action, actionParam)
        if (err):
            self.writeRequestErrorResponse(err)
            return
        self.response.out.write(result)
        return
