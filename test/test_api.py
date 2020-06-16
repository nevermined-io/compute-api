import json

from nevermined_compute_api.constants import BaseURLs
from test.conftest import json_dict


def test_operator(client):
    rv = client.get('/')
    assert json.loads(rv.data.decode('utf-8'))['software'] == 'Nevermined Compute API'


def test_workflow_creation(client):
    rv = client.post(BaseURLs.BASE_OPERATOR_URL + '/init',
                     data=json.dumps(json_dict),
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
