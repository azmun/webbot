from ResolutionStatuses import *
from AmendmentStatuses import *
from ResolutionActions import *
from ActionVerifications import *
from languages import *
import Filt
import pdb

#FIXME: Should the RPC just handle finals?

(RAPPORTEUR_ROLE, RP_ROLE, RPC_ROLE) = range(3)

class NoCommitteeError(Exception):
    pass

class UnknownLanguageError(Exception):
    pass

class UnknownRoleError(Exception):
    pass

def factory(uID, fullName, role, committeeId = None, language = None):
    if role == RAPPORTEUR_ROLE:
        if committeeId == None:
            raise NoCommitteeError()
        return Rapporteur(uID, fullName, committeeId)
    if role == RP_ROLE:
        if not (language in [ENGLISH, SPANISH, BILINGUAL]):
            raise UnknownLanguageError()
        return ResolutionProcessor(uID, fullName, language)
    if role == RPC_ROLE:
        if not (language in [ENGLISH, SPANISH, BILINGUAL]):
            raise UnknownLanguageError()
        return RPC(uID, fullName, language)
    raise UnknownRoleError()

class User:
    def __init__(self, uId, fullName):
        self._uId = uId
        self._fullName = fullName

    def getUId(self):
        return self._uId

    def getFullName(self):
        return self._fullName

    def canCreateResolutionIn(self):
        return None

    def getCommittee(self):
        return None

class Rapporteur(User):
    def __init__(self, uId, fullName, committeeId):
        User.__init__(self, uId, fullName)
        self._committeeId = committeeId

    def getCommittee(self):
        return self._committeeId

    def canCreateResolutionIn(self):
        return self._committeeId

    def getConcernedResolutionsFilter(self):
        return [("committeeId", Filt.EQ, self._committeeId),
                ("status", Filt.IN,[NEW_DRAFT, RETURNED_DRAFT,
            DRAFT_BEING_PROCESSED, ACCEPTED_DRAFT_WAITING_FOR_PRINTING,
            ACCEPTED_DRAFT_BEING_TRANSLATED, PRINTED_DRAFT,
            PASSED_RESOLUTION_BEING_PROCESSED,
            PASSED_RESOLUTION_WAITING_FOR_PRINTING, PRINTED_FINAL_RESOLUTION])]

    def getConcernedResolutionsOrder(self):
        return ["status", "topic", "index"]

    def getResolutionActions(self, status):
        if status == NEW_DRAFT or status == RETURNED_DRAFT:
            return [ActionInfo(actionID = SAVE_RESOLUTION, displayName = "Save", actionFunc = saveResolution, dialog = None, verifications = [VERIFY_ONLY_ONE_IF_BILINGUAL], expectToKeep = True),
                    ActionInfo(actionID = SUBMIT_RESOLUTION, displayName = "Submit", actionFunc = submitResolution, dialog = None, verifications = [VERIFY_ONLY_ONE_IF_BILINGUAL, VERIFY_FULL_RESOLUTION, VERIFY_USER_SURE], expectToKeep = False),
                    ActionInfo(actionID = DELETE_RESOLUTION, displayName = "Delete", actionFunc = deleteResolution, dialog = None, verifications = [VERIFY_USER_SURE], expectToKeep = False)]
        if status == PRINTED_DRAFT:
            return [ActionInfo(actionID = RESOLUTION_PASSED, displayName = "Resolution Passed", actionFunc = resolutionPassed, dialog = None, verifications = [VERIFY_USER_SURE], expectToKeep = False),
                    ActionInfo(actionID = RESOLUTION_FAILED, displayName = "Resolution Failed", actionFunc = resolutionFailed, dialog = None, verifications = [VERIFY_USER_SURE], expectToKeep = False)]
        return []

class ResolutionProcessor(User):
    def __init__(self, uId, fullName, language):
        User.__init__(self, uId, fullName)
        self._language = language

    def getConcernedResolutionsFilter(self):
        return [("assigneeId", Filt.EQ, self._uId),
                ("status", Filt.IN, [DRAFT_BEING_PROCESSED,
            ACCEPTED_DRAFT_BEING_TRANSLATED, PASSED_RESOLUTION_BEING_PROCESSED])]

    def getConcernedResolutionsOrder(self):
        return ["status", "topic", "index"]

    def getResolutionActions(self, status):
        if status == DRAFT_BEING_PROCESSED:
            return [ActionInfo(actionID = ACCEPT_DRAFT, displayName = "Accept", actionFunc = acceptDraft, dialog = None, verifications = [VERIFY_USER_SURE], expectToKeep = False),
                    ActionInfo(actionID = REJECT_DRAFT, displayName = "Return to rapporteur (reject)", actionFunc = rejectDraft, dialog = None, verifications = [VERIFY_USER_SURE_AND_ADDED_COMMENTS], expectToKeep = False)]
        if status == ACCEPTED_DRAFT_BEING_TRANSLATED:
            return [ActionInfo(actionID = TRANSLATION_FINISHED, displayName = "Translation finished", actionFunc = translationFinished, dialog = None, verifications = [VERIFY_RESOLUTIONS_MATCH, VERIFY_USER_SURE], expectToKeep = False)]
        if status == PASSED_RESOLUTION_BEING_PROCESSED:
            return [ActionInfo(actionID = ACCEPT_FINAL, displayName = "Accept", actionFunc = acceptFinal, dialog = None, verifications = [], expectToKeep = False),
                    ActionInfo(actionID = REJECT_FINAL, displayName = "Reject", actionFunc = rejectFinal, dialog = None, verifications = [YOU_HAD_BETTER_BE_REAL_FUCKING_SURE_ABOUT_THIS], expectToKeep = False)]
        return []


class RPC(User):
    def __init__(self, uId, fullName, language):
        User.__init__(self, uId, fullName)

    def getConcernedResolutionsFilter(self):
        return [("assigneeId", Filt.IN, [None, self._uId]),
                ("status", Filt.IN, [DRAFT_BEING_PROCESSED, ACCEPTED_DRAFT_WAITING_FOR_PRINTING,
            ACCEPTED_DRAFT_BEING_TRANSLATED, PASSED_RESOLUTION_WAITING_FOR_PRINTING, SERIOUS_WTF])]

    def getConcernedResolutionsOrder(self):
        return ["status", "topic", "index"]

    def getResolutionActions(self, status):
        if status == DRAFT_BEING_PROCESSED:
            return [ActionInfo(actionID = ASSIGN_DRAFT, displayName = "Assign to Resolution Processor", actionFunc = assignDraft, dialog = PICK_RP, verifications = [], expectToKeep = False),
                    ActionInfo(actionID = ACCEPT_DRAFT, displayName = "Accept", actionFunc = acceptDraft, dialog = None, verifications = [], expectToKeep = False),
                    ActionInfo(actionID = REJECT_DRAFT, displayName = "Reject", actionFunc = rejectDraft, dialog = None, verifications = [], expectToKeep = False)]
        if status == ACCEPTED_DRAFT_WAITING_FOR_PRINTING:
            return [ActionInfo(actionID = DRAFT_PRINTED, displayName = "Draft printed", actionFunc = draftPrinted, dialog = None, verifications = [], expectToKeep = False)]
        if status == ACCEPTED_DRAFT_BEING_TRANSLATED:
            return [ActionInfo(actionID = ASSIGN_FOR_TRANSLATION, displayName = "Assign to Translator", actionFunc = assignForTranslation, dialog = PICK_TRANSLATOR, verifications = [], expectToKeep = False)]
        if status == PASSED_RESOLUTION_WAITING_FOR_PRINTING:
            return [ActionInfo(actionID = FINAL_PRINTED, displayName = "Final printed", actionFunc = finalPrinted, dialog = None, verifications = [], expectToKeep = False)]
        return []
