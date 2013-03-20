from ValidUserRequestHandler import ValidUserRequestHandler
import dblayer
import logging
import pdb

class DoNewTopicHandler(ValidUserRequestHandler):
    def postWithUser(self):
        newTopicEnglish = self.request.get("newTopicEnglish")
        newTopicSpanish = self.request.get("newTopicSpanish")
        if not self.wbUser.canCreateTopics():
            self.writeError('This user cannot create a resolution in this committee.')
            return
        try:
            dblayer.createNextTopic(self.wbUser._committeeId, newTopicEnglish, newTopicSpanish)
        except Exception as e:
            logging.error(e.__repr__())
            self.writeError("Unknown database error.")
            return
        self.redirect('/new_topic')



