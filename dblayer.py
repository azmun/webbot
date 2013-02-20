from google.appengine.ext import db
from google.appengine.api import rdbms
import User
import json
import CommitteeInfo
import Filt
from languages import *
import Utils
from ResolutionInfo import ResolutionInfo
from ResolutionStatuses import *
from CommitteeInfo import CommitteeInfo

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
        return field + "(" + string.join(["%s"] * len(val), ", ") +")"

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
    cursor.execute("SELECT language FROM Committees WHERE committeeId=%s", committeeId)
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
    ret = ResolutionInfo(row[0], json.loads(row[1]), json.loads(row[2]), row[3], row[4], row[5], row[6], row[7], row[8], row[9])
    ret.originalAssigneeId = row[10]
    return ret

def getUserResolutions(user):
    filt = user.getConcernedResolutionsFilter()
    whereString = string.join([_getFilterString(t) for t in filt], " AND ")
    orderString = string.join(user.getConcernedResolutionsOrder(), ", ")
    queryString = "SELECT ownerId, id, serializedResolutionObjectEnglish, serializedResolutionObjectSpanish, committeeId, `status`, `index`, topicIndex, assigneeId, comments, originalAssigneeId FROM Resolutions WHERE " + whereString + " ORDER BY " + orderString
    params = Utils.shallowFlatten([t[2] for t in filt])
    cursor = _getCursor()
    if len(params):
        cursor.execute(queryString, params)
    else:
        cursor.execute(queryString)
    return [ResolutionInfo(row[0], row[1], json.loads(row[2]), json.loads(row[3]), row[4], row[5], row[6], row[7], row[8], row[9], row[10]) for row in cursor.fetchall()]
    
def getEnglishRPs():
    cursor = _getCursor()
    cursor.execute("SELECT id, fullName, role. committeeId FROM Users WHERE language=%s", (ENGLISH,))
    return [Users.factory(row[0], row[1], row[2], row[3], ENGLISH) for row in cursor.fetchall()]

def getSpanishRPs():
    cursor = _getCursor()
    cursor.execute("SELECT id, fullName, role. committeeId FROM Users WHERE language=%s", (SPANISH,))
    return [Users.factory(row[0], row[1], row[2], row[3], SPANISH) for row in cursor.fetchall()]

def getAllCommittees():
    cursor = _getCursor()
    cursor.execute("SELECT language, name, abbreviation, spanishName, englishName FROM Committees LEFT JOIN CommitteeCountries ON Committees.id = CommitteeCountries.committeeId INNER JOIN Countries ON Countries.id = CommitteeCountries.countryId")
    ret = {}
    for row in cursor.fetchall():
        (language, name, abbreviation, spanishName, englishName) = (row[0], row[1], row[2], row[3], row[4])
        if not abbreviation in ret:
            if not language in (ENGLISH, SPANISH, BILINGUAL):
                raise InvalidLanguageError()
            ret[abbreviation] = CommitteeInfo.CommitteeInfo(abbreviation, name, language)
        if language == ENGLISH and englishName:
            ret.countries.append(englishName)
        elif language == SPANISH and spanishName:
            ret.countries.append(spanishName)
        elif language == BILINGUAL and englishName and spanishName:
            ret.countries.append((englishName, spanishName))
    cursor.execute("SELECT abbreviation, englishName, spanishName FROM Committees INNER JOIN CommitteeCountries ON Committees.id = CommitteeCountries.committeeId INNER JOIN Countries ON Countries.id = CommitteeCountries.countryId")
    for row in cursor.fetchall():
        (abbreviation, englishName, spanishName) = (row[0], row[1], row[2])
        lang = ret[abbreviation].language
        if lang == ENGLISH and englishName:
            ret.topics.append(englishName)
        elif lang == SPANISH and spanishName:
            ret.topics.append(spanishName)
        elif lang == BILINGUAL and englishName and spanishName:
            ret.topics.append(englishName, spanishName)
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
    return CommitteeInfo(abbreviation, name, language)

def createNewResolution(committeeId, index, topic, ownerId, language):
    cursor = _getCursor()
    englishRes = None
    spanishRes = None
    if language in [ENGLISH, BILINGUAL]:
        englishResString = json.dumps(Resolution())
    if language in [SPANISH, BILINGUAL]:
        spanishResString = json.dumps(Resolution())
    cursor.execute("INSERT INTO Resolutions (serializedResolutionObjectEnglish, serializedResolutionObjectSpanish, committeeId, `status`, `index`, topicIndex, ownerId) VALUES (%s, %s, %s, %s, %s, %s)", englishResString, spanishResString, committeeId, NEW_DRAFT, index, topic, ownerId)


def getCommitteeUsedIndices(committeeId, topic):
    cursor = _getCursor()
    cursor.execute("SELECT index FROM Resolutions WHERE committeeId=%s AND topic=%s ORDER BY index ASC", committeeId, topic)
    return [row[0] for row in cursor.fetchall()]

def save(ri):
    cursor = _getCursor()
    if (ri.resolutionId != None):
        cursor.execute("UPDATE Resolutions SET ownerID=%s, serializedResolutionObjectEnglish=%s, serializedResolutionObjectSpanish=%s, committeeId=%s, status=%s, index=%s, topicIndex=%s, assigneeId=%s, originalAssigneeId=%s, comments=%s", (ri.ownerId, json.dumps(ri.englishResolution), json.dumps(ri.spanishResolution), ri.committeeId, ri.status, ri.index, ri.topic, ri.assigneeId, ri.originalAssigneeId, ri.comments))
    else:
        cursor.execute("INSERT INTO Resolutions (serializedResolutionObjectEnglish, serializedResolutionObjectSpanish, committeeId, status, index, topicIndex, assigneeId, originalAssigneeId, comments) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (ri.ownerId, json.dumps(ri.resolution), ri.committeeId, ri.status, ri.index, ri.topic, ri.assigneeId, ri.originalAssigneeId, ri.comments))
