import dblayer
import config
import comm
from enums import *

def _saveResolution(ri):
    dblayer.save(ri)

def _submitResolution(ri):
    ri.status = DRAFT_BEING_PROCESSED
    ri.assigneeId = None
    dblayer.save(ri)
    lang = config.committeeLanguage(ri.committeeId)
    comm.push(ri, config.getRPC(lang))

def _deleteResolution(ri):
    dblayer.delete(ri.resolutionId)

def _resolutionPassed(ri):
    ri.status = PASSED_RESOLUTION_BEING_PROCESSED
    dblayer.save(ri)
    lang = config.committeeLanguage(ri.committeeId)
    ri.assigneeId = ri.originalAssigneeId
    if ri.assigneeId == None:
        comm.push(ri, config.getRPC(lang))
    else:
        comm.push(ri, ri.assigneeId)

def _resolutionFailed(ri):
    ri.status = THE_DUSTBIN_OF_HISTORY
    dblayer.save(ri)

def _acceptDraft(ri):
    lang = config.committeeLanguage(ri.committeeId)
    if lang == BILINGUAL
        ri.status = ACCEPTED_DRAFT_BEING_TRANSLATED
        ri.assigneeId = config.getTranslator()
        dblayer.save(ri)
        comm.push(ri, ri.assigneeId)
    else:
        ri.status = ACCEPTED_DRAFT_WAITING_FOR_PRINTING
        ri.assigneeId = None
        dblayer.save(ri)
        comm.push(ri, config.getRPC(lang))

def _rejectDraft(ri):
    ri.status = RETURNED_DRAFT
    dblayer.save(ri)
    comm.push(ri, config.getCommitteeRapporteur(ri.committeeId))

def _translationFinished(ri):
    ri.status = ACCEPTED_DRAFT_WAITING_FOR_PRINTING
    ri.assigneeId = ri.originalAssigneeId
    dblayer.save(ri)
    comm.push(ri, config.getRPC(config.committeeLanguage(ri.committeeId)))

def _acceptFinal(ri):
    ri.status = PASSED_RESOLUTION_WAITING_FOR_PRINTING
    dblayer.save(ri)
    comm.push(ri, config.getRPC(config.comitteeLanguage(ri.committeeId)))

def _rejectFinal(ri):
    ri.status = SERIOUS_WTF
    dblayer.save(ri)
    comm.push(ri, config.getRPC(config.comitteeLanguage(ri.committeeId)))

def _assignDraft(ri, rpParam):
    ri.assigneeId = rpParam
    ri.originalAssigneeId = rpParam
    dblayer.save(ri)
    comm.push(ri, rpParam)

def _draftPrinted(ri):
    ri.status = PRINTED_DRAFT
    dblayer.save(ri)
    user = config.getCommitteeRapporteur(ri.committeeId)
    comm.setMessage(ri, user, "Draft printed!", "The draft resolution {} has been printed; go pick it up!".format(ri.resolutionId))
    comm.push(ri, user)

def _assignForTranslation(ri, translatorParam):
    ri.assignee = translatorParam
    dblayer.save(ri)
    comm.push(ri, translatorParam)

def _finalPrinted(ri):
    ri.status = PRINTED_FINAL_RESOLUTION
    dblayer.save(ri)
    user = config.getCommitteeRapporteur(ri.committeeId)
    comm.setMessage(ri, user, "Final resolution printed!", "The final resolution {} has been printed; go pick it up!".format(ri.resolutionId))
    comm.push(ri, user)
