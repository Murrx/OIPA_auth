import urllib
import urllib2

from django.conf import settings
from django.http import HttpResponse


class AuthenticationMiddleware(object):
    def process_request(self, request):
        token = request.GET.get('token', '')
        auth_request = urllib2.Request(_generate_uri())
        data = {
            "token": token,
            "request": request.path_info,
            "method": request.method,
        }

        auth_request.add_data(urllib.urlencode(data))
        try:
            response = urllib2.urlopen(auth_request)
        except urllib2.HTTPError, err:
            if err.code == 401:
                return HttpResponse('Unauthorized', status=401)
            else:
                raise err
        return None


def _generate_uri():
    host = settings.OIPA_AUTH_SETTINGS['HOST']
    uri = 'http://{0}'.format(host)
    if 'PORT' in settings.OIPA_AUTH_SETTINGS:
        port = settings.OIPA_AUTH_SETTINGS['PORT']
        uri = '{0}:{1}'.format(uri, port)
    uri = '{0}/check-token/'.format(uri)
    return uri
