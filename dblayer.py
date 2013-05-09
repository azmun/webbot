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
import pdb
import copy

conn = None

_INSTANCE_NAME = "arizonamun.org:webbot:azmunrobot"

class NoSuchUserError(Exception):
    pass

class NoSuchResolutionError(Exception):
    pass

class NoSuchCommitteeError(Exception):
    pass

class NoSuchTopicError(Exception):
    pass

class InvalidLanguageError(Exception):
    pass

def _getConnection():
    conn = rdbms.connect(instance=_INSTANCE_NAME, database='webbot')
    return conn


def _getCursor():
    conn = _getConnection()
    return (conn, conn.cursor())


def _getFilterString(tup):
    (field, op, val) = (tup[0], tup[1], tup[2])
    if op == Filt.EQ:
        return field + "<=>%s"
    if op == Filt.IN:
        return '(' + string.join([field + "<=>%s"] * len(val), ' OR ') + ')'

def getRPC_ID(lang):
    if lang == BILINGUAL:
        lang = SPANISH
    conn, cursor = _getCursor()
    cursor.execute("SELECT id FROM Users WHERE role=%s AND language=%s", (User.RPC_ROLE, lang))
    row = cursor.fetchone()
    if not row:
        raise NoSuchUserError()
    return row[0]

def getCommitteeRapporteurID(committeeId):
    conn, cursor = _getCursor()
    cursor.execute("SELECT id FROM Users WHERE committeeId=%s AND role=%s", (committeeId, User.RAPPORTEUR_ROLE))
    row = cursor.fetchone()
    if not row:
        raise NoSuchUserError()
    return row[0]

def getTopicAndCommitteeInfo(topicIndex, committeeId):
    conn, cursor = _getCursor()
    cursor.execute("SELECT `index`, abbreviationEnglish, abbreviationSpanish, displayNameEnglish, displayNameSpanish, englishName, spanishName FROM CommitteeTopics INNER JOIN Committees ON CommitteeTopics.committeeId = Committees.id WHERE Committees.id=%s AND CommitteeTopics.`index`=%s", (committeeId, topicIndex))
    row = cursor.fetchone()
    if not row:
        raise NoSuchTopicError()
    return {"topic": row[0], "committeeAbbreviationEnglish": row[1], "committeeAbbreviationSpanish": row[2], "committeeDisplayNameEnglish": row[3], "committeeDisplayNameSpanish": row[4], "topicEnglishName": row[5], "topicSpanishName": row[6]}

def getCommitteeLanguage(committeeId):
    conn, cursor = _getCursor()
    cursor.execute("SELECT language FROM Committees WHERE id=%s", committeeId)
    row = cursor.fetchone()
    if not row:
        raise NoSuchCommitteeError()
    return row[0]

def getResolutionInfo(resolutionId):
    conn, cursor = _getCursor()
    cursor.execute("SELECT ownerId, serializedResolutionObjectEnglish, serializedResolutionObjectSpanish, committeeId, `status`, Resolutions.`index`, CommitteeTopics.`index`, comments, originalAssigneeId, assigneeId, abbreviationEnglish, abbreviationSpanish, selectedLanguage FROM Resolutions INNER JOIN CommitteeTopics ON Resolutions.topicId = CommitteeTopics.id INNER JOIN Committees ON CommitteeTopics.committeeId = Committees.id WHERE Resolutions.id=%s", resolutionId)
    row = cursor.fetchone()
    if not row:
        raise NoSuchResolutionError()
    ret = ResolutionInfo(ownerId = row[0], englishResolution = None if row[1] == None else json.loads(row[1]), spanishResolution = None if row[2] == None else json.loads(row[2]), committeeId = row[3], status = row[4], index = row[5], topic = row[6], comments = row[7], originalAssigneeId = row[8], resolutionId = resolutionId, assigneeId = row[9], committeeAbbreviationEnglish = row[10], committeeAbbreviationSpanish = row[11])
    ret["selectedLanguage"] = row[12]
    cursor.execute("SELECT englishName, spanishName, englishLongName, spanishLongName, Countries.id FROM Countries INNER JOIN ResolutionSponsors ON Countries.id = ResolutionSponsors.countryId WHERE ResolutionSponsors.resolutionId = %s", resolutionId)
    ret["sponsors"] = []
    for row in cursor.fetchall():
        ret["sponsors"].append({"englishName": row[0], "spanishName": row[1], "englishLongName": row[2], "spanishLongName": row[3], "id": row[4]})
    return ret

def getUserResolutions(user):
    filt = user.getConcernedResolutionsFilter()
    whereString = string.join([_getFilterString(t) for t in filt], " AND ")
    orderString = string.join(["`%s`" % s for s in user.getConcernedResolutionsOrder()], ", ")
    queryString = "SELECT ownerId, Resolutions.id, serializedResolutionObjectEnglish, serializedResolutionObjectSpanish, committeeId, `status`, Resolutions.`index`, CommitteeTopics.`index` AS topic, assigneeId, comments, originalAssigneeId, abbreviationEnglish, abbreviationSpanish, Countries.englishName, Countries.spanishName, englishLongName, spanishLongName, Countries.id AS countryId, selectedLanguage FROM Resolutions LEFT JOIN (ResolutionSponsors INNER JOIN Countries ON ResolutionSponsors.countryId = Countries.id) ON Resolutions.id = ResolutionSponsors.resolutionId INNER JOIN CommitteeTopics ON Resolutions.topicId = CommitteeTopics.id INNER JOIN Committees ON CommitteeTopics.committeeId = Committees.id WHERE " + whereString + " ORDER BY " + orderString
    params = Utils.shallowFlatten([t[2] for t in filt])
    conn, cursor = _getCursor()
    if len(params):
        logging.info("In getUserResolutions; executing cursor with queryString: %s" % queryString)
        logging.info("Params: %s" % params)
        cursor.execute(queryString, params)
    else:
        cursor.execute(queryString)
    ret = {}
    for row in cursor.fetchall():
        (englishName, spanishName, englishLongName, spanishLongName, countryId) = (row[13], row[14], row[15], row[16], row[17])
        if not (row[1] in ret):
            ret[row[1]] = ResolutionInfo(ownerId = row[0], resolutionId = row[1], englishResolution = None if row[2] == None else json.loads(row[2]), spanishResolution = None if row[3] == None else json.loads(row[3]), committeeId = row[4], status = row[5], index = row[6], topic = row[7], assigneeId = row[8], comments = row[9], originalAssigneeId = row[10], committeeAbbreviationEnglish = row[11], committeeAbbreviationSpanish = row[12])
            ret[row[1]]["sponsors"] = []
            ret[row[1]]["selectedLanguage"] = row[18]
        if not countryId is None:
            ret[row[1]]["sponsors"].append({"englishName": englishName, "spanishName": spanishName, "englishLongName": englishLongName, "spanishLongName": spanishLongName, "id": countryId})
    return [ret[key] for key in ret]
    
def getEnglishRPs():
    conn, cursor = _getCursor()
    cursor.execute("SELECT id, fullName, role, committeeId FROM Users WHERE language=%s AND role IN (%s, %s)", (ENGLISH, User.RP_ROLE, User.RPC_ROLE))
    return [User.factory(row[0], row[1], row[2], row[3], ENGLISH) for row in cursor.fetchall()]

def getSpanishRPs():
    conn, cursor = _getCursor()
    cursor.execute("SELECT id, fullName, role, committeeId FROM Users WHERE language=%s AND role IN (%s, %s)", (SPANISH, User.RP_ROLE, User.RPC_ROLE))
    return [User.factory(row[0], row[1], row[2], row[3], SPANISH) for row in cursor.fetchall()]

def userDefinedTopics(committeeId):
    conn, cursor = _getCursor()
    cursor.execute("SELECT userDefinedTopics FROM Committees WHERE id<=>%s", committeeId)
    return cursor.fetchone()[0]

def getAllCommittees():
    conn, cursor = _getCursor()
#FIXME
    cursor.execute("SELECT englishName, spanishName, englishLongName, spanishLongName, id FROM Countries");
    countries = [{"englishName": row[0], "spanishName": row[1], "englishLongName": row[2], "spanishLongName": row[3], "id": row[4]} for row in cursor.fetchall()]
    #cursor.execute("SELECT language, displayNameEnglish, displayNameSpanish, abbreviationEnglish, abbreviationSpanish, spanishName, englishName, Committees.id, Countries.id AS countryId FROM Committees LEFT JOIN CommitteeCountries ON Committees.id = CommitteeCountries.committeeId INNER JOIN Countries ON Countries.id = CommitteeCountries.countryId")
#FIXME this is wrong
    cursor.execute("SELECT abbreviationEnglish, abbreviationSpanish, displayNameEnglish, displayNameSpanish, language, id FROM Committees");
    ret = {}
    for row in cursor.fetchall():
#        (language, displayNameEnglish, displayNameSpanish, abbreviationEnglish,
#                abbreviationSpanish, spanishName, englishName, committeeId, countryId) = (row[0], row[1],
#                        row[2], row[3], row[4], row[5], row[6], row[7], row[8])
#FIXME: this is wrong
        (abbreviationEnglish, abbreviationSpanish, displayNameEnglish, displayNameSpanish, language, committeeId) = (row[0], row[1], row[2], row[3], row[4], row[5])
        if not committeeId in ret:
            if not language in (ENGLISH, SPANISH, BILINGUAL):
                raise InvalidLanguageError()
            ret[committeeId] = {"abbreviationEnglish": abbreviationEnglish,
                    "abbreviationSpanish": abbreviationSpanish,
                    "displayNameEnglish":
                    displayNameEnglish, "displayNameSpanish":
                    displayNameSpanish, "language": language, "countries": [], "topics": []}
            ret[committeeId]["countries"] = copy.deepcopy(countries)
#        ci = ret[committeeId]
#        if language == ENGLISH and englishName:
#            ci["countries"].append({"englishName": englishName, "id": countryId})
#        elif language == SPANISH and spanishName:
#            ci["countries"].append({"spanishName": spanishName, "id": countryId})
#        elif language == BILINGUAL and englishName and spanishName:
#            ci["countries"].append({"englishName": englishName, "spanishName": spanishName, "id": countryId})
    cursor.execute("SELECT abbreviationEnglish, abbreviationSpanish, englishName, spanishName, Committees.id FROM Committees INNER JOIN CommitteeCountries ON Committees.id = CommitteeCountries.committeeId INNER JOIN Countries ON Countries.id = CommitteeCountries.countryId")
    for row in cursor.fetchall():
        (abbreviationEnglish, abbreviationSpanish, englishName, spanishName, committeeId) = (row[0], row[1], row[2], row[3], row[4])
        ci = ret[committeeId]
        lang = ci["language"]
        if lang == ENGLISH and englishName:
            ci["topics"].append(englishName)
        elif lang == SPANISH and spanishName:
            ci["topics"].append(spanishName)
        elif lang == BILINGUAL and englishName and spanishName:
            ci["topics"].append((englishName, spanishName))
    return ret



def getWebbotUserByEmail(email):
    conn, cursor = _getCursor()
    cursor.execute("SELECT id, fullName, role, committeeId, language FROM Users WHERE email=%s", (email,))
    row = cursor.fetchone()
    if not row:
        raise NoSuchUserError()
    (userId, fullName, role, committeeId, language) = (row[0], row[1], row[2], row[3], row[4])
    return User.factory(userId, fullName, role, committeeId, language)

def delete(resolutionId):
    conn, cursor = _getCursor()
    cursor.execute("DELETE FROM Resolutions WHERE id=%s", (resolutionId,))

def getCommitteeHusk(committeeId): # "Husk" because no countries or topics
    conn, cursor = _getCursor()
    cursor.execute("SELECT language, abbreviationEnglish, abbreviationSpanish, displayNameEnglish, displayNameSpanish FROM Committees WHERE id=%s", (committeeId, ))
    row = cursor.fetchone()
    if not row:
        raise NoSuchCommitteeError()
    (language, abbreviationEnglish, abbreviationSpanish, displayNameEnglish, displayNameSpanish) = (row[0], row[1], row[2], row[3], row[4])
    return {"language": language, "abbreviationEnglish": abbreviationEnglish, "abbreviationSpanish": abbreviationSpanish, "displayNameSpanish": displayNameSpanish, "displayNameEnglish": displayNameEnglish}

def getCommitteeTopics(committeeId):
    logging.info("Getting committee topics with id=%s" % committeeId)
    conn, cursor = _getCursor()
    cursor.execute("SELECT englishName, spanishName, `index` FROM CommitteeTopics WHERE committeeId=%s ORDER BY `index`", committeeId)
    return [(row[0], row[1], row[2]) for row in cursor.fetchall()]

def createNewResolution(committeeId, index, topic, ownerId):
    conn, cursor = _getCursor()
    spanishResString = None
    englishResString = None
    language = getCommitteeLanguage(committeeId)
    if language in [ENGLISH, BILINGUAL]:
        englishResString = json.dumps(Resolution.getEmptyResolution())
    if language in [SPANISH, BILINGUAL]:
        spanishResString = json.dumps(Resolution.getEmptyResolution())
    cursor.execute("SELECT id FROM CommitteeTopics WHERE committeeId=%s AND `index`=%s", (committeeId, topic))
    topicRow = cursor.fetchone()
    if not topicRow:
        raise NoSuchTopicError()
    topicId = topicRow[0]
    cursor.execute("INSERT INTO Resolutions (serializedResolutionObjectEnglish, serializedResolutionObjectSpanish, `status`, `index`, topicId, ownerId) VALUES (%s, %s, %s, %s, %s, %s)", (englishResString, spanishResString, NEW_DRAFT, index, topicId, ownerId))
    cursor.close()
    conn.commit()

def createNextTopic(committeeId, english, spanish):
    conn, cursor = _getCursor()
    cursor.execute("INSERT INTO CommitteeTopics (committeeId, `index`, spanishName, englishName) VALUES (%s, (SELECT IFNULL(MAX(`index`), 0) + 1 FROM (SELECT * FROM CommitteeTopics) as FuckMySQL WHERE committeeId=%s), %s, %s)", (committeeId, committeeId, spanish, english))

def getCommitteeUsedIndices(committeeId, topic):
    conn, cursor = _getCursor()
    cursor.execute("SELECT Resolutions.`index` FROM Resolutions INNER JOIN CommitteeTopics ON Resolutions.topicId = CommitteeTopics.id WHERE CommitteeTopics.committeeId=%s AND CommitteeTopics.`index`=%s ORDER BY `index` ASC", (committeeId, topic))
    ret = [row[0] for row in cursor.fetchall()]
    logging.info("Committee %d, topic %d has %d used indices." % (committeeId, topic, len(ret)))
    return ret

def save(ri):
    conn, cursor = _getCursor()
    cursor.execute("SELECT id FROM CommitteeTopics WHERE committeeId=%s AND `index`=%s", (ri["committeeId"], ri["topic"]))
    topicRow = cursor.fetchone()
    if not topicRow:
        raise NoSuchTopicError()
    topicId = topicRow[0]
    sl = ri["selectedLanguage"] if "selectedLanguage" in ri else None
    if (ri["resolutionId"] != None):
        cursor.execute("UPDATE Resolutions SET ownerId=%s, serializedResolutionObjectEnglish=%s, serializedResolutionObjectSpanish=%s, topicId=%s, status=%s, `index`=%s, assigneeId=%s, originalAssigneeId=%s, comments=%s, selectedLanguage=%s WHERE id=%s", (ri["ownerId"], json.dumps(ri["englishResolution"]), json.dumps(ri["spanishResolution"]), topicId, ri["status"], ri["index"], ri["assigneeId"], ri["originalAssigneeId"], ri["comments"], sl, ri["resolutionId"]))
    else:
        cursor.execute("INSERT INTO Resolutions (ownerId, serializedResolutionObjectEnglish, serializedResolutionObjectSpanish, status, `index`, topicId, assigneeId, originalAssigneeId, comments, selectedLanguage) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (ri["ownerId"], json.dumps(ri["englishResolution"]), json.dumps(ri["spanishResolution"]), ri["status"], ri["index"], topicId, ri["assigneeId"], ri["originalAssigneeId"], ri["comments"], sl))
        ri["resolutionId"] = cursor.lastrowid
    cursor.execute("DELETE FROM ResolutionSponsors WHERE resolutionId=%s", ri["resolutionId"])
    sponsorIds = [(ri["resolutionId"], sponsor["id"]) for sponsor in ri["sponsors"]]
    cursor.executemany("INSERT INTO ResolutionSponsors (resolutionId, countryId) VALUES (%s, %s)", sponsorIds)
    cursor.close()
    conn.commit()
