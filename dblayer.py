from google.appengine.ext import db
import User

class NoSuchUserError(Exception):
    pass

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


