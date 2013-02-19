from ValidUserRequestHandler import ValidUserRequestHandler
import dblayer

class NewHandler(ValidUserRequestHandler):
    def getWithUser(self):
        committeeId = self.wbUser.getCommittee()
        if committeeId == None:
            self.response.out.write('<html><body><p>Internal error: no committee.</p></body></html>')
            return
        committee = dblayer.getCommitteeHusk(committeeId)
        committeeOptions = r"""<option value="%d">%s</option>""" % (committeeId, committee.abbreviation)
        usedIndices = dblayer.getCommitteeUsedIndices(committeeId)
        if usedIndices:
            recommended = usedIndices[-1] + 1
        else:
            recommended = 1
        possible = [i for i in range(1, recommended + 5) if i not in usedIndices] #slow
        indexOptions = string.join(['<option value="%d">%d</option>' % (i, i) for i in possible])
        path = os.path.join(os.path.dirname(__file__), 'new_resolution.html')
        self.response.out.write(template.render(path,
            {
                "committeeOptions": committeeOptions,
                "indexOptions": indexOptions
            }))

        


