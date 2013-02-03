from google.appengine.ext import db
from google.appengine.api import rdbms
import User
import json

class NoSuchUserError(Exception):
    pass

class NoSuchResolutionError(Exception):
    pass

def _getConnection():
    return rdbms.connect(instance=_INSTANCE_NAME, databse='webbot')

def _getCursor():
    return _getConnection().cursor()

def getWebbotUserByEmail(email):
    cursor = _getCursor()
    cursor.execute("SELECT id, role, committeeId, language FROM Users WHERE email=%s", (email,))
    row = cursor.fetchone()
    if not row:
        raise NoSuchUserError()
    (userId, role, committeeId, language) = (row[0], row[1], row[2], row[3])
    return User.factory(userId, role, committeeId, language)

def delete(resolutionId):
    cursor = _getCursor()
    cursor.execute("DELETE FROM Resolutions WHERE id=%s", (resolutionId,))


def save(ri):
    cursor = _getCursor()
    if (ri.resolutionId != None):
        cursor.execute("UPDATE Resolutions SET ownerID=%s, serializedResolutionObject=%s, committeeId=%s, status=%s, index=%s, topicIndex=%s, assigneeId=%s, originalAssigneeId=%s, comments=%s", (ri.ownerId, json.dumps(ri.resolution), ri.committeeId, ri.status, ri.index, ri.topic, ri.assigneeId, ri.originalAssigneeId, ri.comments))
    else:
        cursor.execute("INSERT INTO Resolutions (serializedResolutionObject, committeeId, status, index, topicIndex, assigneeId, originalAssigneeId, comments) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (ri.ownerId, json.dumps(ri.resolution), ri.committeeId, ri.status, ri.index, ri.topic, ri.assigneeId, ri.originalAssigneeId, ri.comments))
