import dblayer
import comm
import collections
import pdb

ActionInfo = collections.namedtuple("ActionInfo",
        ["actionID", "displayName", "actionFunc", "dialog", "verifications", "expectToKeep"])

(SAVE_RESOLUTION, SUBMIT_RESOLUTION, DELETE_RESOLUTION, RESOLUTION_PASSED, RESOLUTION_FAILED, ACCEPT_DRAFT, REJECT_DRAFT, TRANSLATION_FINISHED, ACCEPT_FINAL, REJECT_FINAL, ASSIGN_DRAFT, DRAFT_PRINTED, ASSIGN_FOR_TRANSLATION, FINAL_PRINTED) = range(14)

def getSerializableVersion(ra):
    return {"actionID": ra.actionID, "displayName": ra.displayName, "dialog": ra.dialog, "verifications": ra.verifications, "expectToKeep": ra.expectToKeep}

def saveResolution(ri, unused):
    dblayer.save(ri)

def submitResolution(ri, unused):
    pdb.set_trace()
    ri["status"] = DRAFT_BEING_PROCESSED
    ri["assigneeId"] = None
    lang = dblayer.getCommitteeLanguage(ri["committeeId"])
    usr = dblayer.getRPC_ID(lang)
    ri["ownerID"] = usr
    dblayer.save(ri)
    comm.push(ri, usr)

def deleteResolution(ri, unused):
    dblayer.delete(ri["resolutionId"])

def resolutionPassed(ri, unused):
    ri["status"] = PASSED_RESOLUTION_BEING_PROCESSED
    lang = dblayer.getCommitteeLanguage(ri["committeeId"])
    ri["assigneeId"] = ri["originalAssigneeId"]
    if ri["assigneeId"] == None:
        ri["ownerId"] = dblayer.getRPC_ID(lang)
    else:
        ri["ownerId"] = ri["assigneeId"]
    dblayer.save(ri)
    comm.push(ri, ri["ownerId"])

def resolutionFailed(ri, unused):
    ri["status"] = THE_DUSTBIN_OF_HISTORY
    ri["ownerId"] = None
    dblayer.save(ri)

def acceptDraft(ri, unused):
    lang = dblayer.getCommitteeLanguage(ri["committeeId"])
    if lang == BILINGUAL:
        ri["status"] = ACCEPTED_DRAFT_BEING_TRANSLATED
    else:
        ri["status"] = ACCEPTED_DRAFT_WAITING_FOR_PRINTING
    ri["assigneeId"] = None
    ri["ownerId"] = dblayer.getRPC_ID(lang)
    dblayer.save(ri)
    comm.push(ri, ri["ownerId"])

def rejectDraft(ri, unused):
    ri["status"] = RETURNED_DRAFT
    usr = dblayer.getCommitteeRapporteurID(ri["committeeId"])
    ri["ownerId"] = usr
    dblayer.save(ri)
    comm.push(ri, usr)

def translationFinished(ri, unused):
    ri["status"] = ACCEPTED_DRAFT_WAITING_FOR_PRINTING
    ri["assigneeId"] = ri["originalAssigneeId"]
    ri["ownerId"] = dblayer.getRPC_ID(dblayer.getCommitteeLanguage(ri["committeeId"]))
    dblayer.save(ri)
    comm.push(ri, ri["ownerId"])

def acceptFinal(ri, unused):
    ri["status"] = PASSED_RESOLUTION_WAITING_FOR_PRINTING
    ri["ownerId"] = dblayer.getRPC_ID(dblayer.getCommitteeLanguage(ri["committeeId"]))
    dblayer.save(ri)
    comm.push(ri, ri["ownerId"])

def rejectFinal(ri, unused):
    ri["status"] = SERIOUS_WTF
    ri["ownerId"] = dblayer.getRPC_ID(dblayer.getCommitteeLanguage(ri["committeeId"]))
    dblayer.save(ri)
    comm.push(ri, ri["ownerId"])

def assignDraft(ri, rpParam):
    ri["assigneeId"] = rpParam
    ri["originalAssigneeId"] = rpParam
    ri["ownerId"] = rpParam
    dblayer.save(ri)
    comm.push(ri, rpParam)

def draftPrinted(ri, unused):
    ri["status"] = PRINTED_DRAFT
    user = dblayer.getCommitteeRapporteurID(ri["committeeId"])
    ri["ownerId"] = user
    dblayer.save(ri)
    comm.setMessage(ri, user, "Draft printed!", "The draft resolution {} has been printed; go pick it up!".format(ri["resolutionId"]))
    comm.push(ri, user)

def assignForTranslation(ri, translatorParam):
    ri["assigneeId"] = translatorParam
    ri["ownerId"] = translatorParam
    dblayer.save(ri)
    comm.push(ri, translatorParam)

def finalPrinted(ri, unused):
    ri["status"] = PRINTED_FINAL_RESOLUTION
    user = dblayer.getCommitteeRapporteurID(ri["committeeId"])
    ri["ownerId"] = user
    dblayer.save(ri)
    comm.setMessage(ri, user, "Final resolution printed!", "The final resolution {} has been printed; go pick it up!".format(ri["resolutionId"]))
    comm.push(ri, user)
