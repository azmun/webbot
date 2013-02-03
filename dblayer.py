from google.appengine.ext import db
import User
import json

class NoSuchUserError(Exception):
    pass

class NoSuchResolutionError(Exception):
    pass

def _ResolutionModel(db.model):
    ownerId = db.IntegerProperty()
    serializedResolutionObject = db.TextProperty()
    committeeId = db.IntegerProperty()
    status = db.IntegerProperty()
    index = db.IntegerProperty()
    topicIndex = db.IntegerProperty()
    assigneeId = db.IntegerProperty()
    originalAssigneeId = db.IntegerProperty()
    comments = db.TextProperty()

def _UserModel(db.Model):
    email = db.EmailProperty()
    role = db.IntegerProperty()
    committeeId = db.IntegerProperty()
    language = db.IntegerProperty()

def getWebbotUserByEmail(email):
    q = _UserModel.all()
    q.filter('email =', email)
    result = q.get()
    if not result:
        raise NoSuchUserError()
    ps = result.properties()
    try:
        committeeId = ps["committeeId"]
    except KeyError:
        committeeId = None
    try:
        language = ps["language"]
    except KeyError:
        language = None
    return User.factory(result.key().id(), ps["role"], committeeId, language)

def delete(resolutionId):
    k = db.Key.from_path('_ResolutionModel', resolutionId)
    db.delete(k)

def save(ri):
    if (ri.resolutionId != None):
        m = _ResolutionModel(key = db.Key.from_path('_ResolutionModel', ri.resolutionId),
                ownerId = ri.ownerId,
                serializedResolutionObject = json.dumps(ri.resolution),
                committeeId = ri.committeeId,
                status = ri.status,
                index = ri.index,
                topicIndex = ri.topic
                assigneeId = ri.assigneeId
                originalAssigneeId = ri.originalAssigneeId
                comments = ri.comments)
    else:
        m = _ResolutionModel(ownerId = ri.ownerId,
                serializedResolutionObject = json.dumps(ri.resolution),
                committeeId = ri.committeeId,
                status = ri.status,
                index = ri.index,
                topicIndex = ri.topic
                assigneeId = ri.assigneeId
                originalAssigneeId = ri.originalAssigneeId
                comments = ri.comments)
    m.put()

