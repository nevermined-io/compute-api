import json
from urllib.request import urlopen
from pathlib import Path

import pytest

from nevermined_compute_api.run import app

app = app


@pytest.fixture
def client():
    client = app.test_client()
    yield client


@pytest.fixture
def coordinator_json():
    path = Path(__file__).parent / "data/ddo.fl-coordinator-consumer.json"
    with path.open() as f:
        yield f.read()


@pytest.fixture
def participant_json():
    path = Path(__file__).parent / "data/ddo.fl-participant-workflow.json"
    with path.open() as f:
        yield f.read()


workflow_ddo = json.loads(urlopen(
    "https://raw.githubusercontent.com/keyko-io/nevermined-docs/master/architecture/specs"
    "/examples/metadata/v0.1/ddo-example-workflow.json").read().decode(
    'utf-8'))

json_dict = {
    "serviceAgreementId": "bb23s87856d59867503f80a690357406857698570b964ac8dcc9d86da4ada010",
    "workflow": workflow_ddo
}
