from ValidUserRequestHandler import ValidUserRequestHandler
import dblayer

class DoNewHandler(ValidUserRequestHandler):
    def writeCommitteeFail(self):
        self.writeError('No valid committee selected.')
    def postWithUser(self):
        committeeIdStr = self.request.get("committee")
        indexStr = self.request.get("index")
        topicStr = self.request.get("topic")
        try:
            topic = int(topicStr, base=10)
        except:
            self.writeError("No valid topic selected.")
            return
        try:
            committeeId = int(committeeIdStr, base=10)
        except:
            self.writeCommitteeFail()
            return
        try:
            index = int(indexStr, base=10)
        except:
            self.writeError('No valid index selected.')
            return
        if self.wbUser.canCreateResolutionIn() != committeeId:
            self.writeError('This user cannot create a resolution in this committee.')
            return
        try:
            dblayer.createNewResolution(committeeId, index, topic, wbUser.uID)
        except:
            self.writeError("Unknown database error.")
            return
        self.redirect('/')



