from ValidUserRequestHandler import ValidUserRequestHandler
import json
import dblayer

class NewHandler(ValidUserRequestHandler):
    def getTopicIndexOptions(self, topic):
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
        committeeOptions = r"""<option value="%d">%s</option>""" % (committeeId, committee.abbreviation)
        topics = dblayer.getCommitteeTopics(committeeId)
        indexOptions = json.dumps([self.getTopicIndexOptions(i) for i in range(len(topics))])
        path = os.path.join(os.path.dirname(__file__), 'new_resolution.html')
        topicOptions = string.join(['<option value="%d">%s</option>' for idx, val in enumerate(topics)])
        self.response.out.write(template.render(path,
            {
                "committeeOptions": committeeOptions,
                "indexOptions": indexOptions,
                "topicOptions": topicOptions
            }))

        


