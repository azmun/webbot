from ValidUserRequestHandler import ValidUserRequestHandler
from ValidUserRequestHandler import SUCCESS

USER_NOT_ADMIN = SUCCESS + 1
class ValidAdminUserRequestHandler(ValidUserRequestHandler):

    def validateUser(self, user):
        return SUCCESS if user.isAdmin() else USER_NOT_ADMIN
        
    def getValidationErrorMsg(self, validationCode):
        if validationCode == USER_NOT_ADMIN:
            return "Only an administrator may view this page."
