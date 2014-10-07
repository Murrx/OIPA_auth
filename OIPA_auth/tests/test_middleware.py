from OIPA_auth.middleware import _generate_uri
from django.conf import settings
import pytest


def setup_module():
    settings.configure(OIPA_AUTH_SETTINGS={'HOST': 'localhost', 'PORT': '8080'})


@pytest.mark.parametrize("input,expected", [
    ({'HOST': 'localhost', 'PORT': '8080'}, 'http://localhost:8080/check-token/'),
    ({'HOST': 'localhost', }, 'http://localhost/check-token/'),
])
def test__generate_uri(input, expected):
    settings.OIPA_AUTH_SETTINGS = input
    _generate_uri()
    assert(_generate_uri() == expected)
