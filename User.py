from ResolutionStatuses import *
from AmendmentStatuses import *
from ResolutionModel import *
from AmendmentModel import *
from ResolutionActions import *

#FIXME: Should the RPC just handle finals?

class User:
    def __init__(self, uId):
        self._uId = uId

    def getUId(self):
        return self._uId

class Rapporteur(User):
    def __init__(self, uId, committeeId):
        super(Rapporteur, self).__init__(uId)
        self._committeeId = committeeId

    def getConcernedResolutionsQuery(self):
        q = ResolutionModel.all()
        q.filter("committeeId =", self._committeeId)
        q.filter("status IN", [NEW_DRAFT, RETURNED_DRAFT,
            DRAFT_BEING_PROCESSED, ACCEPTED_DRAFT_WAITING_FOR_PRINTING,
            ACCEPTED_DRAFT_BEING_TRANSLATED, PRINTED_DRAFT,
            PASSED_RESOLUTION_BEING_PROCESSED,
            PASSED_RESOLUTION_WAITING_FOR_PRINTING, PRINTED_FINAL_RESOLUTION])
        q.order("status")
        q.order("topic")
        q.order("draft")
        q.order("index")
        return q

    def getConcernedAmendmentsQuery(self):
        q = AmendmentModel.all()
        q.filter("committeeId =", self._committeeId)
        q.filter("status IN", [NEW_AMENDMENT, RETURNED_AMENDMENT,
            AMENDMENT_BEING_PROCESSED, ACCEPTED_AMENDMENT_WAITING_FOR_PRINTING,
            ACCEPTED_AMENDMENT_BEING_TRANSLATED, PRINTED_AMENDMENT])
        q.order("resolutionId")
        q.order("index")
        return q

    def getResolutionActions(self, status):
        if status == NEW_DRAFT or status == RETURNED_DRAFT:
            return [("Save", _saveResolution, None, [], True),
                    ("Submit", _submitResolution, None, [VERIFY_FULL_RESOLUTION, VERIFY_USER_SURE], False),
                    ("Delete", _deleteResolution, None, [VERIFY_USER_SURE], False)]
        if status == PRINTED_DRAFT:
            return [("Resolution Passed", _resolutionPassed, None, [VERIFY_NO_OUTSTANDING_AMENDMENTS, VERIFY_USER_SURE], False),
                    ("Resolution Failed", _resolutionFailed, None, [VERIFY_USER_SURE], False)]
        return None

class ResolutionProcessor(User):
    def __init__(self, uId, language):
        super(ResolutionProcessor, self).__init__(uId)
        self._language = language

    def getConcernedResolutionsQuery(self):
        q = ResolutionModel.all()
        q.filter("assigneeId =", self._uId)
        q.filter("status IN", [DRAFT_BEING_PROCESSED,
            ACCEPTED_DRAFT_BEING_TRANSLATED, PASSED_RESOLUTION_BEING_PROCESSED])
        q.order("status")
        q.order("topic")
        q.order("draft")
        q.order("index")
        return q

    def getResolutionActions(self, status):
        if status == DRAFT_BEING_PROCESSED:
            return [("Accept", _acceptDraft, None, [VERIFY_USER_SURE], False),
                    ("Return to rapporteur (reject)", _rejectDraft, None, [VERIFY_USER_SURE_AND_ADDED_COMMENTS], False)]
        if status == ACCEPTED_DRAFT_BEING_TRANSLATED:
            return [("Translation finished", _translationFinished, None, [VERIFY_RESOLUTIONS_MATCH, VERIFY_USER_SURE], False)]
        if status == PASSED_RESOLUTION_BEING_PROCESSED:
            return [("Accept", _acceptFinal, None, [], False),
                    ("Reject", _rejectFinal, None, [YOU_HAD_BETTER_BE_REAL_FUCKING_SURE_ABOUT_THIS], False)] 
        return None


class RPC(User):
    def __init__(self, uId, language):
        super(RPC, self).__init__(uId, language)

    def getConcernedResolutionsQuery(self):
        q = ResolutionModel.all()
        q.filter("assigneeId =", None)
        q.filter("status IN", [DRAFT_BEING_PROCESSED, ACCEPTED_DRAFT_WAITING_FOR_PRINTING,
            ACCEPTED_DRAFT_BEING_TRANSLATED, PASSED_RESOLUTION_WAITING_FOR_PRINTING, SERIOUS_WTF])
        q.order("status")
        q.order("topic")
        q.order("draft")
        q.order("index")
        return q

    def getResolutionActions(self, status):
        if status == DRAFT_BEING_PROCESSED:
            return [("Assign to Resolution Processor", _assignDraft, PICK_RP, [], False),
                    ("Accept", _acceptDraft, None, [], False),
                    ("Reject", _rejectDraft, None, [], False)]
        if status == ACCEPTED_DRAFT_WAITING_FOR_PRINTING:
            return [("Draft printed", _draftPrinted, None, [], False)]
        if status == ACCEPTED_DRAFT_BEING_TRANSLATED:
            return [("Assign to Resolution Processor", _assignForTranslation, PICK_TRANSLATOR, [], False)]
        if status == PASSED_RESOLUTION_WAITING_FOR_PRINTING:
            return [("Final printed", _finalPrinted, None, [], False)]
        return None
