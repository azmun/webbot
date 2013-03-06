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
        abbr = committee["abbreviationEnglish"] if committee["language"] == ENGLISH else committee["abbreviationSpanish"]
        committeeOptions = '<option value="%d">%s</option>' % (committeeId, abbr)
        topics = dblayer.getCommitteeTopics(committeeId)
        indexOptions = {tup[2]: self.getTopicIndexOptions(tup[2], committeeId) for tup in topics}
        indexOptionsStr = json.dumps(indexOptions)
        path = os.path.join(os.path.dirname(__file__), 'new_resolution.html')
        if committee["language"] == ENGLISH:
            topicNames = [t[0] for t in topics]
        else:
            topicNames = [t[1] for t in topics]
        topicIndices = [t[2] for t in topics]
        topicOptions = string.join(['<option value="%d">%d) %s</option>' % (idx, idx, val) for val, idx in zip(topicNames, topicIndices)])
        if len(indexOptions) > 0:
            firstTopicIndexOptions = indexOptions[topics[0][2]]
        else:
            firstTopicIndexOptions = ''
        self.response.out.write(template.render(path,
            {
                "firstTopicIndexOptions": firstTopicIndexOptions,
                "committeeOptions": committeeOptions,
                "indexOptions": indexOptionsStr,
                "topicOptions": topicOptions
            }))

        


