import pytest
from nevermined_compute_api.run import app
from pathlib import Path

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


json_dict = """{
  "serviceAgreementId": "bb23s87856d59867503f80a690357406857698570b964ac8dcc9d86da4ada010",
  "workflow": {
    "@context": "https://w3id.org/future-method/v1",
    "authentication": [],
    "created": "2019-04-09T19:02:11Z",
    "id": "did:nv:bda17c126f5a411c8edd94cd0700e466a860f269a0324b77ae37d04cf84bb894",
    "proof": {
      "created": "2019-04-09T19:02:11Z",
      "creator": "0x00Bd138aBD70e2F00903268F3Db08f2D25677C9e",
      "signatureValue": "1cd57300733bcbcda0beb59b3e076de6419c0d7674e7befb77820b53c79e3aa8f1776effc64cf088bad8cb694cc4d71ebd74a13b2f75893df5a53f3f318f6cf828",
      "type": "DDOIntegritySignature"
    },
    "publicKey": [
      {
        "id": "did:nv:60000f48357a42fbb8d6ff3a25a23413e9cc852db091485eb89506a5fed9f33c",
        "owner": "0x00Bd138aBD70e2F00903268F3Db08f2D25677C9e",
        "type": "EthereumECDSAKey"
      }
    ],
    "service": [
      {
        "attributes": {
          "main": {
            "dateCreated": "2012-10-10T17:00:00Z",
            "datePublished": "2019-04-09T19:02:11Z",
            "type": "workflow"
          },
          "workflow": {
            "stages": [
              {
                "index": 0,
                "input": [
                  {
                    "id": "did:nv:b06d19edca5b4b17b7ee0cdee9718d97a4790cc520234037b78d27b4169e7fc7",
                    "index": 0
                  },
                  {
                    "id": "did:nv:b06d19edca5b4b17b7ee0cdee9718d97a4790cc520234037b78d27b4169e7fc7",
                    "index": 1
                  }
                ],
                "output": {
                  "accessProxyUrl": "https://gateway.com",
                  "brizoAddress": "0xfEF2d5e1670342b9EF22eeeDcb287EC526B48095",
                  "metadata": {
                    "name": "Workflow output"
                  },
                  "metadataUrl": "https://metadata.com",
                  "secretStoreUrl": "https://secret-store.duero.nevermined.com"
                },
                "requirements": {
                  "container": {
                    "checksum": "sha256:cb57ecfa6ebbefd8ffc7f75c0f00e57a7fa739578a429b6f72a0df19315deadc",
                    "image": "openjdk",
                    "tag": "14-jdk"
                  },
                  "serverInstances": 1
                },
                "stageType": "Filtering",
                "transformation": {
                  "id": "did:nv:eee5a8ac40454b139b5cb1aceb425e7adfaa0b0742704a5d8041bde081b632ec"
                }
              }
            ]
          }
        },
        "index": "0",
        "serviceEndpoint": "https://gateway.com/api/v1/aquarius/assets/ddo/{did}",
        "type": "Metadata"
      }
    ]
  }
}"""
