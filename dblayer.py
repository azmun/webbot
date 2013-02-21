from google.appengine.ext import db
from google.appengine.api import rdbms
import User
import logging
import json
import string
import Filt
from languages import *
import Utils
from ResolutionInfo import ResolutionInfo
from ResolutionStatuses import *
import Resolution

conn = None

_INSTANCE_NAME = "arizonamun.org:webbot:data"

class NoSuchUserError(Exception):
    pass

class NoSuchResolutionError(Exception):
    pass

class NoSuchCommitteeError(Exception):
    pass

class InvalidLanguageError(Exception):
    pass

def _getConnection():
    if conn:
        return conn
    return rdbms.connect(instance=_INSTANCE_NAME, database='webbot')

def _getCursor():
    return _getConnection().cursor()

def _getFilterString(tup):
    (field, op, val) = (tup[0], tup[1], tup[2])
    if op == Filt.EQ:
        return field + "=%s"
    if op == Filt.IN:
        return "`%s` IN (" % field + string.join(["%s"] * len(val), ", ") +")"

def getRPC_ID(lang):
    cursor = _getCursor()
    cursor.execute("SELECT id FROM Users WHERE role=%s AND language=%s", (User.RPC, lang))
    row = cursor.fetchone()
    if not row:
        raise NoSuchUserError()
    return row[0]

def getCommitteeRapporteurID(committeeId):
    cursor = _getCursor()
    cursor.execute("SELECT id FROM Users WHERE committeeId=%s AND role=%s", (committeeId, User.RAPPORTEUR))
    row = cursor.fetchone()
    if not row:
        raise NoSuchUserError()
    return row[0]

def getCommitteeLanguage(committeeId):
    cursor = _getCursor()
    cursor.execute("SELECT language FROM Committees WHERE id=%s", committeeId)
    row = cursor.fetchone()
    if not row:
        raise NoSuchCommitteeError()
    return row[0]

def getResolutionInfo(resolutionId):
    cursor = _getCursor()
    cursor.execute("SELECT ownerId, serializedResolutionObjectEnglish, serializedResolutionObjectSpanish, committeeId, `status`, `index`, topicIndex, comments, originalAssigneeId FROM Resolutions WHERE id=%s", resolutionId)
    row = cursor.fetchone()
    if not row:
        raise NoSuchResolutionError()
    ret = ResolutionInfo(ownerId = row[0], englishResolution = None if row[1] == None else json.loads(row[1]), spanishResolution = None if row[2] == None else json.loads(row[2]), committeeId = row[3], status = row[4], index = row[5], topic = row[6], comments = row[7], originalAssigneeId = row[8], resolutionId = resolutionId)
    return ret

def getUserResolutions(user):
    filt = user.getConcernedResolutionsFilter()
    whereString = string.join([_getFilterString(t) for t in filt], " AND ")
    orderString = string.join(["`%s`" % s for s in user.getConcernedResolutionsOrder()], ", ")
    queryString = "SELECT ownerId, id, serializedResolutionObjectEnglish, serializedResolutionObjectSpanish, committeeId, `status`, `index`, topicIndex, assigneeId, comments, originalAssigneeId FROM Resolutions WHERE " + whereString + " ORDER BY " + orderString
    params = Utils.shallowFlatten([t[2] for t in filt])
    cursor = _getCursor()
    if len(params):
        logging.info("In getUserResolutions; executing cursor with queryString: %s" % queryString)
        cursor.execute(queryString, params)
    else:
        cursor.execute(queryString)
    return [ResolutionInfo(ownerId = row[0], resolutionId = row[1], englishResolution = None if row[2] == None else json.loads(row[2]), spanishResolution = None if row[3] == None else json.loads(row[3]), committeeId = row[4], status = row[5], index = row[6], topic = row[7], assigneeId = row[8], comments = row[9], originalAssigneeId = row[10]) for row in cursor.fetchall()]
    
def getEnglishRPs():
    cursor = _getCursor()
    cursor.execute("SELECT id, fullName, role, committeeId FROM Users WHERE language=%s", (ENGLISH,))
    return [User.factory(row[0], row[1], row[2], row[3], ENGLISH) for row in cursor.fetchall()]

def getSpanishRPs():
    cursor = _getCursor()
    cursor.execute("SELECT id, fullName, role, committeeId FROM Users WHERE language=%s", (SPANISH,))
    return [User.factory(row[0], row[1], row[2], row[3], SPANISH) for row in cursor.fetchall()]

def getAllCommittees():
    cursor = _getCursor()
    cursor.execute("SELECT language, name, abbreviation, spanishName, englishName, Committees.id FROM Committees LEFT JOIN CommitteeCountries ON Committees.id = CommitteeCountries.committeeId INNER JOIN Countries ON Countries.id = CommitteeCountries.countryId")
    ret = {}
    for row in cursor.fetchall():
        (language, name, abbreviation, spanishName, englishName, committeeId) = (row[0], row[1], row[2], row[3], row[4], row[5])
        if not abbreviation in ret:
            if not language in (ENGLISH, SPANISH, BILINGUAL):
                raise InvalidLanguageError()
            ret[committeeId] = {"abbreviation": abbreviation, "name": name, "language": language, "countries": [], "topics": []}
        ci = ret[committeeId]
        if language == ENGLISH and englishName:
            ci["countries"].append(englishName)
        elif language == SPANISH and spanishName:
            ci["countries"].append(spanishName)
        elif language == BILINGUAL and englishName and spanishName:
            ci["countries"].append((englishName, spanishName))
    cursor.execute("SELECT abbreviation, englishName, spanishName, Committees.id FROM Committees INNER JOIN CommitteeCountries ON Committees.id = CommitteeCountries.committeeId INNER JOIN Countries ON Countries.id = CommitteeCountries.countryId")
    for row in cursor.fetchall():
        (abbreviation, englishName, spanishName, committeeId) = (row[0], row[1], row[2], row[3])
        ci = ret[committeeId]
        lang = ci["language"]
        if lang == ENGLISH and englishName:
            ci["topics"].append(englishName)
        elif lang == SPANISH and spanishName:
            ci["topics"].append(spanishName)
        elif lang == BILINGUAL and englishName and spanishName:
            ci["topics"].append(englishName, spanishName)
    return ret



def getWebbotUserByEmail(email):
    cursor = _getCursor()
    cursor.execute("SELECT id, fullName, role, committeeId, language FROM Users WHERE email=%s", (email,))
    row = cursor.fetchone()
    if not row:
        raise NoSuchUserError()
    (userId, fullName, role, committeeId, language) = (row[0], row[1], row[2], row[3], row[4])
    return User.factory(userId, fullName, role, committeeId, language)

def delete(resolutionId):
    cursor = _getCursor()
    cursor.execute("DELETE FROM Resolutions WHERE id=%s", (resolutionId,))

def getCommitteeHusk(committeeId): # "Husk" because no countries or topics
    cursor = _getCursor()
    cursor.execute("SELECT language, abbreviation, name FROM Committees WHERE id=%s", (committeeId, ))
    row = cursor.fetchone()
    if not row:
        raise NoSuchCommitteeError()
    (language, abbreviation, name) = (row[0], row[1], row[2])
    return {"language": language, "abbreviation": abbreviation, "name": name}

def getCommitteeTopics(committeeId):
    logging.info("Getting committee topics with id=%s" % committeeId)
    cursor = _getCursor()
    cursor.execute("SELECT englishName, spanishName FROM CommitteeTopics WHERE committeeId=%s ORDER BY `index`", committeeId)
    return [(row[0], row[1]) for row in cursor.fetchall()]

def createNewResolution(committeeId, index, topic, ownerId):
    cursor = _getCursor()
    spanishResString = None
    englishResString = None
    language = getCommitteeLanguage(committeeId)
    if language in [ENGLISH, BILINGUAL]:
        englishResString = json.dumps(Resolution.getEmptyResolution())
    if language in [SPANISH, BILINGUAL]:
        spanishResString = json.dumps(Resolution.getEmptyResolution())
    cursor.execute("INSERT INTO Resolutions (serializedResolutionObjectEnglish, serializedResolutionObjectSpanish, committeeId, `status`, `index`, topicIndex, ownerId) VALUES (%s, %s, %s, %s, %s, %s, %s)", (englishResString, spanishResString, committeeId, NEW_DRAFT, index, topic, ownerId))


def getCommitteeUsedIndices(committeeId, topic):
    cursor = _getCursor()
    cursor.execute("SELECT `index` FROM Resolutions WHERE committeeId=%s AND topicIndex=%s ORDER BY `index` ASC", (committeeId, topic))
    return [row[0] for row in cursor.fetchall()]

def save(ri):
    cursor = _getCursor()
    if (ri.resolutionId != None):
        cursor.execute("UPDATE Resolutions SET ownerID=%s, serializedResolutionObjectEnglish=%s, serializedResolutionObjectSpanish=%s, committeeId=%s, status=%s, `index`=%s, topicIndex=%s, assigneeId=%s, originalAssigneeId=%s, comments=%s", (ri.ownerId, json.dumps(ri.englishResolution), json.dumps(ri.spanishResolution), ri.committeeId, ri.status, ri.index, ri.topic, ri.assigneeId, ri.originalAssigneeId, ri.comments))
    else:
        cursor.execute("INSERT INTO Resolutions (serializedResolutionObjectEnglish, serializedResolutionObjectSpanish, committeeId, status, `index`, topicIndex, assigneeId, originalAssigneeId, comments) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (ri.ownerId, json.dumps(ri.resolution), ri.committeeId, ri.status, ri.index, ri.topic, ri.assigneeId, ri.originalAssigneeId, ri.comments))
