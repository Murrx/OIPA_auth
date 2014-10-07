import urllib
import urllib2
from django.conf import settings

class AuthenticationMiddleware(object):

    def process_request(self, request):
        token = request.GET.get('token', '')
        auth_request = urllib2.Request("http://{0}:{1}/check-token/".format(
            settings.OIPA_AUTH_SETTINGS['HOST'],
            settings.OIPA_AUTH_SETTINGS['PORT'])
        )
        data = {
            "token": token,
            "request": request.path_info,
            "method": request.method,
        }

        auth_request.add_data(urllib.urlencode(data))
        response = urllib2.urlopen(auth_request)

        #Prints the response
        # import pprint
        # import json
        # response_parsed = json.loads(response.read())
        # pp = pprint.PrettyPrinter(indent=4)
        # pp.pprint(response_parsed)
        return None
