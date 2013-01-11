from ValidUserRequestHandler import ValidUserRequestHandler
from google.appengine.ext.webapp import template
import json
import os
import dblayer
import string
import pdb
import Enums

from languages import *

class NewTopicHandler(ValidUserRequestHandler):
    def getWithUser(self):
        committeeId = self.wbUser.getCommittee()
        if committeeId == None:
            self.response.out.write('<html><body><p>Internal error: no committee.</p></body></html>')
            return
        currentTopics = [{"index": row[2], "englishName": row[0], "spanishName": row[1]} for row in dblayer.getCommitteeTopics(committeeId)]
        languageName = Enums.Reverse["language"][dblayer.getCommitteeLanguage(committeeId)]
        path = os.path.join(os.path.dirname(__file__), 'new_topic.html')
        self.response.out.write(template.render(path,
            {
                "languageName": json.dumps(languageName),
                "currentTopics": json.dumps(currentTopics)
            }));

        


