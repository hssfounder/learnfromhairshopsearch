from .. import create_app
from ..provider.models import Address
import pytest

@pytest.fixture(scope="module")
def app():
    return create_app()

@pytest.fixture(scope="module")
def a():
    return Address(street_1="403 S Second",
            street_2="",
            city="Clarksville",
            state="TN",
            zip_code="37040")

def test_new_address(a):
    assert isinstance(a, Address)
    assert a.city       == "Clarksville"
    assert a.street_1   == "403 S Second"

def test_address_json(a):
    assert a.to_json() == {
            'city': 'Clarksville',
            'provider_id': None,
            'apartment': None,
            'state': 'TN',
            'street_1': '403 S Second',
            'street_2': '',
            'zip_code': '37040'
            }

def test_geocode(a, app):
    with app.app_context():
        resp = a.geocode()

    # geocode 403 S Second Clarksville TN 37040
    assert [(36.52451, -87.357699)] == resp
