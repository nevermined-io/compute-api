import os
from pathlib import Path
import json

from contracts_lib_py.utils import get_account
from common_utils_py.ddo.ddo import DDO
from nevermined_sdk_py import Nevermined, Config
import yaml
from configparser import ConfigParser

config_parser = ConfigParser()
configuration = config_parser.read('config.ini')
GROUP = config_parser.get('resources', 'group')  # str | The custom resource's group name
VERSION = config_parser.get('resources', 'version')  # str | The custom resource's version
NAMESPACE = config_parser.get('resources', 'namespace')  # str | The custom resource's namespace
KEYFILE = json.loads(Path(os.getenv("PROVIDER_KEYFILE")).read_text())


def create_execution(service_agreement_id, workflow):
    """Creates the argo workflow template

    Args:
        service_agreement_id (str): The id of the service agreement being executed
        workflow (dict): The workflow submitted to the compute api

    Returns:
        dict: The workflow template filled by the compute api with all the parameters

    """
    ddo = DDO(dictionary=workflow)
    workflow_template = get_workflow_template()

    workflow_template['apiVersion'] = GROUP + '/' + VERSION
    workflow_template['metadata']['namespace'] = NAMESPACE
    workflow_template['spec']['arguments']['parameters'] += create_arguments(ddo)
    workflow_template["spec"]["workflowMetadata"]["labels"][
        "serviceAgreementId"] = service_agreement_id

    if ddo.metadata["main"]["type"] == "fl-coordinator":
        workflow_template["spec"]["entrypoint"] = "coordinator-workflow"
    else:
        workflow_template["spec"]["entrypoint"] = "compute-workflow"

    return workflow_template


def create_arguments(ddo):
    """Create the arguments that need to be add to the argo template.

    Args:
        ddo (:py:class:`common_utils_py.ddo.ddo.DDO`): The workflow DDO.

    Returns:
        list: The list of arguments to be appended to the argo workflow

    """
    args = ''
    image = ''
    tag = ''

    if ddo.metadata["main"]["type"] != "fl-coordinator":
        workflow = ddo.metadata["main"]["workflow"]

        options = {
            "resources": {
                "metadata.url": "http://172.17.0.1:5000",
            },
            "keeper-contracts": {
                "keeper.url": "http://172.17.0.1:8545"
            }
        }
        config = Config(options_dict=options)
        nevermined = Nevermined(config)

        # TODO: Currently this only supports one stage
        transformation_did = workflow["stages"][0]["transformation"]["id"]
        transformation_ddo = nevermined.assets.resolve(transformation_did)
        transformation_metadata = transformation_ddo.get_service("metadata")

        # get args and container
        args = transformation_metadata.main["algorithm"]["entrypoint"]
        image = transformation_metadata.main["algorithm"]["requirements"]["container"]["image"]
        tag = transformation_metadata.main["algorithm"]["requirements"]["container"]["tag"]

    arguments = [
        {
            "name": "credentials",
            # remove white spaces
            "value": json.dumps(KEYFILE, separators=(",", ":"))
        },
        {
            "name": "password",
            "value": os.getenv("PROVIDER_PASSWORD")
        },
        {
            "name": "metadata_url",
            "value": "http://172.17.0.1:5000"
        },
        {
            "name": "gateway_url",
            "value": "http://172.17.0.1:8030"
        },
        {
            "name": "node",
            "value": "http://172.17.0.1:8545"
        },
        {
            "name": "secret_store_url",
            "value": "http://172.17.0.1:12001"
        },
        {
            "name": "workflow",
            "value": f"did:nv:{ddo.asset_id[2:]}"
        },
        {
            "name": "verbose",
            "value": "false"
        },
        {
            "name": "transformation_container_image",
            "value": f"{image}:{tag}"
        },
        {
            "name": "transformation_arguments",
            "value": args
        }
    ]
    return arguments


def setup_keeper():
    init_account_envvars()
    account = get_account(0)
    if account is None:
        raise AssertionError(f'Nevermined Gateway cannot run without a valid '
                             f'ethereum account. Account address was not found in the environment'
                             f'variable `PROVIDER_ADDRESS`. Please set the following evnironment '
                             f'variables and try again: `PROVIDER_ADDRESS`, `PROVIDER_PASSWORD`, '
                             f', `PROVIDER_KEYFILE`, `RSA_KEYFILE` and `RSA_PASSWORD`.')
    if not account.key_file and not (account.password and account.key_file):
        raise AssertionError(f'Nevermined Gateway cannot run without a valid '
                             f'ethereum account with either a password and '
                             f'keyfile/encrypted-key-string '
                             f'or private key. Current account has password {account.password}, '
                             f'keyfile {account.key_file}, encrypted-key {account._encrypted_key} '
                             f'and private-key {account._private_key}.')


def init_account_envvars():
    os.environ['PARITY_ADDRESS'] = os.getenv('PROVIDER_ADDRESS', '')
    os.environ['PARITY_PASSWORD'] = os.getenv('PROVIDER_PASSWORD', '')
    os.environ['PARITY_KEYFILE'] = os.getenv('PROVIDER_KEYFILE', '')
    os.environ['PSK-RSA_PRIVKEY_FILE'] = os.getenv('RSA_PRIVKEY_FILE', '')
    os.environ['PSK-RSA_PUBKEY_FILE'] = os.getenv('RSA_PUBKEY_FILE', '')


def get_workflow_template():
    """Returns a pre configured argo workflow template.

    Returns:
        dict: argo workflow template

    """
    path = Path(__file__).parent / "argo-workflow.yaml"
    with path.open() as f:
        workflow_template = yaml.safe_load(f)

    return workflow_template
