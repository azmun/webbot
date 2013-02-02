import dblayer
import config
import comm
from enums import *

def _saveResolution(ri, unused):
    dblayer.save(ri)

def _submitResolution(ri, unused):
    ri.status = DRAFT_BEING_PROCESSED
    ri.assigneeId = None
    lang = config.committeeLanguage(ri.committeeId)
    usr = config.getRPC(lang)
    ri.ownerID = usr
    dblayer.save(ri)
    comm.push(ri, usr)

def _deleteResolution(ri, unused):
    dblayer.delete(ri.resolutionId)

def _resolutionPassed(ri, unused):
    ri.status = PASSED_RESOLUTION_BEING_PROCESSED
    lang = config.committeeLanguage(ri.committeeId)
    ri.assigneeId = ri.originalAssigneeId
    if ri.assigneeId == None:
        ri.ownerId = config.getRPC(lang)
    else:
        ri.ownerId = ri.assigneeId
    dblayer.save(ri)
    comm.push(ri.ownerId)

def _resolutionFailed(ri, unused):
    ri.status = THE_DUSTBIN_OF_HISTORY
    ri.ownerId = None
    dblayer.save(ri)

def _acceptDraft(ri, unused):
    lang = config.committeeLanguage(ri.committeeId)
    if lang == BILINGUAL
        ri.status = ACCEPTED_DRAFT_BEING_TRANSLATED
        ri.assigneeId = config.getTranslator()
        ri.ownerId = ri.assigneeId
        dblayer.save(ri)
    else:
        ri.status = ACCEPTED_DRAFT_WAITING_FOR_PRINTING
        ri.assigneeId = None
        ri.ownerId = config.getRPC(lang)
        dblayer.save(ri)
    comm.push(ri, ri.ownerId)

def _rejectDraft(ri, unused):
    ri.status = RETURNED_DRAFT
    usr = config.getCommitteeRapporteur(ri.committeeId)
    ri.ownerId = usr
    dblayer.save(ri)
    comm.push(ri, usr)

def _translationFinished(ri, unused):
    ri.status = ACCEPTED_DRAFT_WAITING_FOR_PRINTING
    ri.assigneeId = ri.originalAssigneeId
    ri.ownerId = config.getRPC(config.committeeLanguage(ri.committeeId))
    dblayer.save(ri)
    comm.push(ri, ri.ownerId)

def _acceptFinal(ri, unused):
    ri.status = PASSED_RESOLUTION_WAITING_FOR_PRINTING
    ri.ownerId = config.getRPC(config.committeeLanguage(ri.committeeId))
    dblayer.save(ri)
    comm.push(ri, ri.ownerId)

def _rejectFinal(ri, unused):
    ri.status = SERIOUS_WTF
    ri.ownerId = config.getRPC(config.committeeLanguage(ri.committeeId))
    dblayer.save(ri)
    comm.push(ri, ri.ownerId)

def _assignDraft(ri, rpParam):
    ri.assigneeId = rpParam
    ri.originalAssigneeId = rpParam
    ri.ownerId = rpParam
    dblayer.save(ri)
    comm.push(ri, rpParam)

def _draftPrinted(ri, unused):
    ri.status = PRINTED_DRAFT
    user = config.getCommitteeRapporteur(ri.committeeId)
    ri.ownerId = user
    dblayer.save(ri)
    comm.setMessage(ri, user, "Draft printed!", "The draft resolution {} has been printed; go pick it up!".format(ri.resolutionId))
    comm.push(ri, user)

def _assignForTranslation(ri, translatorParam):
    ri.assigneeId = translatorParam
    ri.ownerId = translatorParam
    dblayer.save(ri)
    comm.push(ri, translatorParam)

def _finalPrinted(ri, unused):
    ri.status = PRINTED_FINAL_RESOLUTION
    user = config.getCommitteeRapporteur(ri.committeeId)
    ri..ownerId = user
    dblayer.save(ri)
    comm.setMessage(ri, user, "Final resolution printed!", "The final resolution {} has been printed; go pick it up!".format(ri.resolutionId))
    comm.push(ri, user)
