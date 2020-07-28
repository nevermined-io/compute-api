import json
from urllib.request import urlopen
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def env_setup(monkeypatch):
    monkeypatch.setenv("PROVIDER_ADDRESS", "0x00bd138abd70e2f00903268f3db08f2d25677c9e")
    monkeypatch.setenv("PROVIDER_PASSWORD", "node0")

    provider_keyfile = Path(__file__).parent / "resources/data/publisher_key_file.json"
    monkeypatch.setenv("PROVIDER_KEYFILE", provider_keyfile.as_posix())


@pytest.fixture
def client():
    # This import is done here so that the `env_setup` fixture is called before we
    # initialize the flask app (since it requires the env variables
    from nevermined_compute_api.run import app

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
