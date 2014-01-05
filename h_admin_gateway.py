from ValidAdminUserRequestHandler import ValidAdminUserRequestHandler
from google.appengine.ext.webapp import template
import json
import os
import dblayer
import string
import pdb
from collections import namedtuple
from languages import *

Link = namedtuple('Link', ['name', 'url'])
LINKS = [
    Link('Users', '/admin/users'),
    Link('Resolutions', '/admin/resolutions'),
    Link('Countries', '/admin/countries'),
    Link('Committees and Topics', '/admin/committes')
]

class AdminGatewayHandler(ValidAdminUserRequestHandler):
    def getWithUser(self):
        path = os.path.join(os.path.dirname(__file__), 'admin_gateway.html')
        self.response.out.write(template.render(path,
            {
                'links': LINKS
            }))

        


