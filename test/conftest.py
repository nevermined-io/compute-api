import pytest
from nevermined_compute_api.run import app

app = app


@pytest.fixture
def client():
    client = app.test_client()
    yield client