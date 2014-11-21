from ..consumer.models import Consumer
import pytest

def test_consumer_status_update():
    c = Consumer()
    c.status = 'Hey bro'
    assert c.status == 'Hey bro'
