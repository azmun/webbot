from ValidUserRequestHandler import ValidUserRequestHandler
from google.appengine.ext.webapp import template
import json
import os
import dblayer
import string
import pdb
from languages import *

class NewHandler(ValidUserRequestHandler):
    def getTopicIndexOptions(self, topic, committeeId):
        usedIndices = dblayer.getCommitteeUsedIndices(committeeId, topic)
        if usedIndices:
            recommended = usedIndices[-1] + 1
        else:
            recommended = 1
        possible = [i for i in range(1, recommended + 5) if i not in usedIndices] #slow
        return string.join(['<option value="%d">%d</option>' % (i, i) for i in possible])
        
    def getWithUser(self):
        committeeId = self.wbUser.getCommittee()
        if committeeId == None:
            self.response.out.write('<html><body><p>Internal error: no committee.</p></body></html>')
            return
        committee = dblayer.getCommitteeHusk(committeeId)
        committeeOptions = '<option value="%d">%s</option>' % (committeeId, committee["abbreviation"])
        topics = dblayer.getCommitteeTopics(committeeId)
        indexOptions = [self.getTopicIndexOptions(i, committeeId) for i in range(len(topics))]
        indexOptionsStr = json.dumps(indexOptions)
        path = os.path.join(os.path.dirname(__file__), 'new_resolution.html')
        if committee["language"] == ENGLISH:
            topicNames = [t[0] for t in topics]
        else:
            topicNames = [t[1] for t in topics]
        topicOptions = string.join(['<option value="%d">%d) %s</option>' % (idx, idx, val) for idx, val in enumerate(topicNames)])
        if len(indexOptions) > 0:
            firstTopicIndexOptions = indexOptions[0]
        else:
            firstTopicIndexOptions = ''
        self.response.out.write(template.render(path,
            {
                "firstTopicIndexOptions": firstTopicIndexOptions,
                "committeeOptions": committeeOptions,
                "indexOptions": indexOptionsStr,
                "topicOptions": topicOptions
            }))

        


