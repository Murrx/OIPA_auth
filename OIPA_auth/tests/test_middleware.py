from OIPA_auth.middleware import _generate_sso_host_uri, _generate_request_uri
from django.conf import settings
import pytest


def setup_module():
    settings.configure(OIPA_AUTH_SETTINGS={'HOST': 'localhost', 'PORT': '8080'})


@pytest.mark.parametrize("input,expected", [
    ({'HOST': 'localhost', 'PORT': '8080'}, 'http://localhost:8080/'),
    ({'HOST': 'localhost', }, 'http://localhost/'),
])
def test__generate_sso_host_uri(input, expected):
    settings.OIPA_AUTH_SETTINGS = input
    _generate_sso_host_uri()
    assert(_generate_sso_host_uri() == expected)


@pytest.mark.parametrize("input,expected", [
    ('test', 'http://localhost/test/'),
])
def test__generate_request_uri(input, expected):
    assert(_generate_request_uri(input) == expected)

