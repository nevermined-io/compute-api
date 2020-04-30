import json

import pytest


@pytest.mark.skip(reason="Failing some times with actions")
def test_operator(client):
    rv = client.get('/')
    assert json.loads(rv.data.decode('utf-8'))['software'] == 'Operator service'
