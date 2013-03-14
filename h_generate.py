import dblayer
import languages
import pdb
from ValidUserRequestHandler import ValidUserJSONHandler
from generate_document import generate_document
from ResolutionStatuses import isDraft
class GenerateDocumentHandler(ValidUserJSONHandler):
    def getWithUser(self):
        resolutionId = int(self.request.get('id'))
        lang = int(self.request.get('language'))
        ri = dblayer.getResolutionInfo(resolutionId)
        tAndC = dblayer.getTopicAndCommitteeInfo(ri["topic"], ri["committeeId"])
        if lang == languages.ENGLISH:
            res = ri["englishResolution"]
            topicName = tAndC["topicEnglishName"]
            committeeSalutationName = tAndC["committeeDisplayNameEnglish"]
            committeeAbbr = tAndC["committeeAbbreviationEnglish"]
        elif lang == languages.SPANISH:
            res = ri["spanishResolution"]
            topicName = tAndC["topicSpanishName"]
            committeeSalutationName = tAndC["committeeDisplayNameSpanish"]
            committeeAbbr = tAndC["committeeAbbreviationSpanish"]
        document = generate_document(res, lang, topicName, committeeSalutationName, committeeAbbr, ri["index"], tAndC["topic"], isDraft(ri["status"]), ri["sponsors"])
        self.response.headers['Content-Type'] = 'application/vnd.oasis.opendocument.text'
        self.response.headers['Content-Disposition'] = "attachment; filename=res.fodt"
        self.response.out.write(document)

