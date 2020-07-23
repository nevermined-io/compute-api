import json

import pytest

from nevermined_compute_api.constants import BaseURLs
from test.conftest import json_dict


@pytest.mark.skip(reason="Failing some times with actions")
def test_operator(client):
    rv = client.get('/')
    assert json.loads(rv.data.decode('utf-8'))['software'] == 'Operator service'


def test_workflow_creation(client):
    rv = client.post(BaseURLs.BASE_OPERATOR_URL + '/init',
                     data=json_dict,
                     content_type='application/json')
    assert rv.status_code == 200
    id = rv.data.decode()

    list = client.get(BaseURLs.BASE_OPERATOR_URL + '/list',
                      content_type='application/json')

    assert 'nevermined-compute-' in id
    assert id in list.json
    client.delete(BaseURLs.BASE_OPERATOR_URL + '/stop/' + id,
                  data=None,
                  content_type='application/json')


def test_coordinator_workflow(client, coordinator_json):
    rv = client.post(BaseURLs.BASE_OPERATOR_URL + '/init',
                     data=coordinator_json,
                     content_type='application/json')

    assert rv.status_code == 200

    id_ = rv.data.decode()

    list_ = client.get(BaseURLs.BASE_OPERATOR_URL + '/list',
                       content_type='application/json')

    assert 'nevermined-compute-' in id_
    assert id_ in list_.json
    client.delete(BaseURLs.BASE_OPERATOR_URL + '/stop/' + id_,
                  data=None,
                  content_type='application/json')
