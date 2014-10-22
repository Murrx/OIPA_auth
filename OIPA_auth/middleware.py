import urllib
import urllib2

from django.conf import settings
from django.http import HttpResponse


class AuthenticationMiddleware(object):
    def process_view(self, request, view_func, view_args, view_kwargs):
        """Handles user authentication. If the provided token is invalid a 401(unauthorized) response is returned"""
        if _call_blacklisted(view_kwargs):
            request.valid_token = _authenticate_user(request.GET.get('token', ''))
        return None if (not _call_blacklisted(view_kwargs) or request.valid_token) \
            else HttpResponse('Unauthorized', status=401)


class AuthorizationMiddleware(object):
    def process_view(self, request, view_func, view_args, view_kwargs):
        """Handles user authorization. If SSO authorization fails a 401 response is returned"""
        if _call_blacklisted(view_kwargs) and request.valid_token:
            auth_request = urllib2.Request(_generate_request_uri('authorize-call'))
            data = {
                "token": request.GET.get('token', ''),
                "request": request.path_info,
                "method": request.method,
            }
            auth_request.add_data(urllib.urlencode(data))
            _send_request(auth_request)
            return None
        else:
            return HttpResponse('Unauthorized', status=401) if _call_blacklisted(view_kwargs) else None


def _authenticate_user(token):
    """Authenticate the user based on the provided token"""
    auth_request = urllib2.Request(_generate_request_uri('validate-token'))
    data = {
        "token": token,
    }
    auth_request.add_data(urllib.urlencode(data))
    try:
        _send_request(auth_request)
    except urllib2.HTTPError, err:
        if err.code == 401:
            return False
        else:
            raise err
    return True


def _generate_request_uri(function_path):
    """Generate a uri for the request based on function called"""
    return '{0}{1}'.format(_generate_sso_host_uri(), _generate_function_path(function_path))


def _generate_sso_host_uri():
    """Generates uri for the sso_host based on django settings"""
    host = settings.OIPA_AUTH_SETTINGS['HOST']
    uri = 'http://{0}'.format(host)
    if 'PORT' in settings.OIPA_AUTH_SETTINGS:
        port = settings.OIPA_AUTH_SETTINGS['PORT']
        uri = '{0}:{1}'.format(uri, port)
    return '{0}/'.format(uri)


def _generate_function_path(function_path):
    return '{0}/'.format(function_path)


def _call_blacklisted(view_kwargs):
    """Determines if a call is blacklisted or not"""
    return 'api_name' in view_kwargs


def _send_request(request):
    """simple encapsulation of the urllib.urlopen method call"""
    return urllib2.urlopen(request)