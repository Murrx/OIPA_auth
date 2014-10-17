import urllib
import urllib2

from django.conf import settings
from django.http import HttpResponse


class AuthenticationMiddleware(object):
    def process_view(self, request, view_func, view_args, view_kwargs):
        if _call_blacklisted(view_kwargs):
            request.valid_token = False
            token = request.GET.get('token', '')
            auth_request = urllib2.Request(_generate_uri('check-token'))
            data = {
                "token": token,
                "request": request.path_info,
                "method": request.method,
            }
            auth_request.add_data(urllib.urlencode(data))
            try:
                urllib2.urlopen(auth_request)
                request.valid_token = True
            except urllib2.HTTPError, err:
                if err.code == 401:
                    return HttpResponse('Unauthorized', status=401)
                else:
                    raise err
        return None


class AuthorizationMiddleware(object):
    def process_view(self, request, view_func, view_args, view_kwargs):
        if _call_blacklisted(view_kwargs) and request.valid_token:
            reg_request = urllib2.Request(_generate_uri('register-call'))
            data = {
                "request": request.path_info,
                "method": request.method,
            }
            reg_request.add_data(urllib.urlencode(data))
            urllib2.urlopen(reg_request)
            return None
        elif not _call_blacklisted(view_kwargs):
            return None
        elif not request.valid_token:
            return HttpResponse('Unauthorized', status=401)


def _generate_uri(function_path):
    host = settings.OIPA_AUTH_SETTINGS['HOST']
    uri = 'http://{0}'.format(host)
    if 'PORT' in settings.OIPA_AUTH_SETTINGS:
        port = settings.OIPA_AUTH_SETTINGS['PORT']
        uri = '{0}:{1}'.format(uri, port)
    uri = '{0}/{1}/'.format(uri, function_path)
    return uri

def _call_blacklisted(view_kwargs):
    return 'api_name' in view_kwargs
