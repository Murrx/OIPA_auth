import urllib2
import pytest

from django.conf import settings
from django.http import HttpRequest

from OIPA_auth import middleware


def setup_module():
    settings.configure(OIPA_AUTH_SETTINGS={'HOST': 'localhost', 'PORT': '8080'})

NOT_BLACKLISTED = {}
BLACKLISTED = {u'api_name': u'v3', u'resource_name': u'activities'}
VALID_TOKEN_LAMBDA = lambda x: True
INVALID_TOKEN_LAMBDA = lambda x: False
NONE_LAMBDA = lambda x: None
UNAUTHORIZED401_LAMBDA = lambda x: _raise_(urllib2.HTTPError(code=401, msg='unauthorized', url='', hdrs=None, fp=None))
TIMEOUT408_LAMBDA = lambda x: _raise_(urllib2.HTTPError(code=408, msg='Request timeout', url='', hdrs=None, fp=None))


@pytest.mark.parametrize("view_kwargs,token_lambda,expected", [
    #should return None if call is not blacklisted
    (NOT_BLACKLISTED, INVALID_TOKEN_LAMBDA, None),
    # #should return None if call is blacklisted and token is valid
    (BLACKLISTED, VALID_TOKEN_LAMBDA, None),
    # #should return 401 if call is blacklisted and token is invalid
    (BLACKLISTED, INVALID_TOKEN_LAMBDA, 401),
])
def test_authenticationmiddleware__process_view(monkeypatch, view_kwargs, token_lambda, expected):
    monkeypatch.setattr(middleware, '_authenticate_user', token_lambda)
    if expected is None:
        assert middleware.AuthenticationMiddleware().process_view(HttpRequest(), {}, {}, view_kwargs) == expected
    else:
        assert middleware.AuthenticationMiddleware().process_view(HttpRequest(), {}, {}, view_kwargs).status_code == expected


@pytest.mark.parametrize("view_kwargs,valid_token,expected", [
    #should return None if call is not blacklisted
    (NOT_BLACKLISTED, False, None),
    # should return None if call is blacklisted and api key is validated
    (BLACKLISTED, True, None),
    # should return 401 if call is blacklisted and user does not have a valid api key
    (BLACKLISTED, False, 401),
])
def test_authorizationmiddleware__process_view(monkeypatch, view_kwargs, valid_token, expected):
    monkeypatch.setattr(middleware, '_send_request', lambda x: None)
    request = HttpRequest()
    request.valid_token = valid_token
    if expected is None:
        assert middleware.AuthorizationMiddleware().process_view(request, {}, {}, view_kwargs) == expected
    else:
        assert middleware.AuthorizationMiddleware().process_view(request, {}, {}, view_kwargs).status_code == expected


@pytest.mark.parametrize("function,expected", [
    #should return True if url open returns a 200(OK) response
    (NONE_LAMBDA, True),
    #should return False if SSO sends a 401 response
    (UNAUTHORIZED401_LAMBDA, False),
])
def test__authenticate_user(monkeypatch, function, expected):
    monkeypatch.setattr(middleware, '_send_request', function)
    assert middleware._authenticate_user('dummy_token') == expected


@pytest.mark.parametrize("function,expected", [
    #should raise an exception when any other exception occurs while validating the token
    (TIMEOUT408_LAMBDA, False),
])
def test__authenticate_user_exception(monkeypatch, function, expected):
    with pytest.raises(urllib2.HTTPError):
        monkeypatch.setattr(middleware, '_send_request', function)
        assert middleware._authenticate_user('dummy_token') == expected


@pytest.mark.parametrize("input,expected", [
    #Only 'HOST' is provided so result should be 'http://localhost/'
    ({'HOST': 'localhost', }, 'http://localhost/'),
    #Only 'HOST' and PORT is provided so result should be 'http://localhost:8080/'
    ({'HOST': 'localhost', 'PORT': '8080'}, 'http://localhost:8080/'),
])
def test__generate_sso_host_uri(input, expected):
    settings.OIPA_AUTH_SETTINGS = input
    middleware._generate_sso_host_uri()
    assert(middleware._generate_sso_host_uri() == expected)


@pytest.mark.parametrize("view_kwargs,expected", [
    #'view_kwargs' contains the key 'api_name' and so it should return True
    (BLACKLISTED, True),
    # 'view_kwargs' does not contain the key 'api_name' and so it should return False
    (NOT_BLACKLISTED, False),
])
def test__call_blacklisted(view_kwargs, expected):
    assert middleware._call_blacklisted(view_kwargs) == expected


def _raise_(ex):
    raise ex