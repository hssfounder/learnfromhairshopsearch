from ..app.provider.models import Provider
#import pytest

@pytest.fixture('module')
def p():
    return Provider()

def test_provider_acceptable_business_url(p):
    assert p
