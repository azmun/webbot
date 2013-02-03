from google.appengine.ext import db
import User

class NoSuchUserError(Exception):
    pass

class NoSuchResolutionError(Exception):
    pass

def _ResolutionModel(db.model):
    ownerId = db.IntegerProperty()
    serializedResolutionObject = db.TextObject()
    committeeId = db.IntegerProperty()
    status = db.IntegerProperty()
    index = db.IntegerProperty()
    topicIndex = db.IntegerProperty()
    assigneeId = db.IntegerProperty()
    originalAssigneeId = db.IntegerProperty()

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
