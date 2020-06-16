import json
from urllib.request import urlopen

import pytest

from nevermined_compute_api.run import app

app = app


@pytest.fixture
def client():
    client = app.test_client()
    yield client


workflow_ddo = json.loads(urlopen(
    "https://raw.githubusercontent.com/keyko-io/nevermined-docs/master/architecture/specs"
    "/examples/metadata/v0.1/ddo-example-workflow.json").read().decode(
    'utf-8'))

json_dict = {
    "serviceAgreementId": "bb23s87856d59867503f80a690357406857698570b964ac8dcc9d86da4ada010",
    "workflow": workflow_ddo
}
