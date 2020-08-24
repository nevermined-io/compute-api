import os
from pathlib import Path

from contracts_lib_py.utils import get_account
from nevermined_sdk_py import Nevermined, Config
import yaml


def create_arguments(ddo):
    workflow = ddo.metadata['main']['workflow']
    account = get_provider_account()
    arguments = dict()
    arguments['parameters'] = []
    arguments['parameters'].append({'name': 'credentials',
                                    'value': '{"id":"50aa801a-8d66-1402-1fa4-d8987868c2ce",'
                                             '"version":3,"crypto":{"cipher":"aes-128-ctr",'
                                             '"cipherparams":{'
                                             '"iv":"a874e6fe50a5bb088826c45560dc1b7e"},'
                                             '"ciphertext":"2383c6aa50c744b6558e77b5dcec6137f647c81f10f71f22a87321fd1306056c","kdf":"pbkdf2","kdfparams":{"c":10240,"dklen":32,"prf":"hmac-sha256","salt":"eca6ccc9fbb0bdc3a516c7576808ba5031669e6878f3bb95624ddb46449e119c"},"mac":"14e9a33a45ae32f88a0bd5aac14521c1fcf14f56fd55c1a1c080b2f81ddb8d44"},"address":"068ed00cf0441e4829d9784fcbe7b9e26d4bd8d0","name":"","meta":"{}"}'})
    arguments['parameters'].append({'name': 'password', 'value': 'secret'})
    arguments['parameters'].append({'name': 'inputs', 'value': '/data/input_folder'})
    arguments['parameters'].append(
        {'name': 'transformations', 'value': '/data/transformations_folder'})
    arguments['parameters'].append({'name': 'volume', 'value': '/data'})
    arguments['parameters'].append({'name': 'node', 'value': 'http://172.17.0.1:8545'})
    arguments['parameters'].append({'name': 'verbose', 'value': 'false'})
    arguments['parameters'].append({'name': 'workflow', 'value': f'did:nv:{ddo.asset_id[2:]}'})

    # arguments['parameters'].append({'name': 'metadata_url', 'value': workflow['stages'][0][
    # 'output']['metadataUrl']})
    arguments['parameters'].append({'name': 'metadata_url', 'value': 'http://172.17.0.1:5000'})
    arguments['parameters'].append({'name': 'gateway_url', 'value': 'http://172.17.0.1:8030'})
    # arguments['parameters'].append({'name': 'gateway_url', 'value': workflow['stages'][0][
    # 'output']['accessProxyUrl']})
    arguments['parameters'].append(
        {'name': 'secret_store_url', 'value': 'http://172.17.0.1:12001'})
    # arguments['parameters'].append({'name': 'secret_store_url', 'value': workflow['stages'][0][
    # 'output']['secretStoreUrl']})
    return arguments


def create_volume_claim_templates():
    voloume_dict = [dict()]
    voloume_dict[0]['metadata'] = dict()
    voloume_dict[0]['metadata']['name'] = 'workdir'
    voloume_dict[0]['spec'] = dict()
    voloume_dict[0]['spec']['accessModes'] = ["ReadWriteMany"]
    voloume_dict[0]['spec']['resources'] = dict()
    voloume_dict[0]['spec']['resources']['requests'] = dict()
    voloume_dict[0]['spec']['resources']['requests']['storage'] = '2Gi'
    return voloume_dict


def create_templates(ddo):
    templates = [dict()]
    templates[0]['name'] = 'compute-workflow'
    templates[0]['dag'] = dict()
    templates[0]['dag']['tasks'] = []
    templates[0]['dag']['tasks'].append({'name': 'configurator', 'template': 'configuratorPod'})

    if ddo.metadata["main"]["type"] == "fl-coordinator":
        d = get_coordinator_execution_template()
        templates[0]['dag']['tasks'] += d["templates"][1]["dag"]["tasks"]
        templates[0]['dag']['tasks'].append({'name': 'publishing', 'template': 'publishingPod', 'dependencies': ['coordinator', 'aggregator']})
    else:
        templates[0]['dag']['tasks'].append({'name': 'transformation', 'template': 'transformationPod', 'dependencies': ['configurator']})
        templates[0]['dag']['tasks'].append({'name': 'publishing', 'template': 'publishingPod', 'dependencies': ['transformation']})
    templates.append({'name': 'configuratorPod', 'container': create_configuration_container()})
    if ddo.metadata["main"]["type"] == "fl-coordinator":
        templates.append(create_execute_coordinator())
    else:
        templates.append({'name': 'transformationPod', 'container': create_execute_container(ddo)})
    templates.append({'name': 'publishingPod', 'container': create_publishing_container()})
    return templates


def create_configuration_container():
    config_pod = dict()
    config_pod['name'] = 'configuratorPod'
    config_pod['image'] = 'keykoio/nevermined-pod-config-py'
    config_pod['imagePullPolicy'] = 'IfNotPresent'
    config_pod['command'] = ['sh', '-cxe']
    # config_pod['args'] = ["tail -f /dev/null"]
    config_pod['args'] = ["cp -rv /artifacts ./artifacts;\
         ls -l; \
         mkdir $VOLUME/adminlogs/; \
         pod-config \
         --workflow $WORKFLOW \
         --path $VOLUME \
         --credentials $CREDENTIALS \
         --password $PASSWORD \
         --node $NODE \
         --gateway-url $GATEWAY_URL \
         --metadata-url $METADATA_URL \
         --secretstore-url $SECRET_STORE_URL; \
         ls -lR /data"]
    config_pod['env'] = []
    config_pod['env'].append(
        {'name': 'CREDENTIALS', 'value': '{{workflow.parameters.credentials}}'})
    config_pod['env'].append(
        {'name': 'PASSWORD', 'value': '{{workflow.parameters.password}}'})
    config_pod['env'].append(
        {'name': 'VOLUME', 'value': '{{workflow.parameters.volume}}'})
    config_pod['env'].append({'name': 'NODE', 'value': '{{workflow.parameters.node}}'})
    config_pod['env'].append({'name': 'WORKFLOW', 'value': '{{workflow.parameters.workflow}}'})
    config_pod['env'].append(
        {'name': 'GATEWAY_URL', 'value': '{{workflow.parameters.gateway_url}}'})
    config_pod['env'].append(
        {'name': 'METADATA_URL', 'value': '{{workflow.parameters.metadata_url}}'})
    config_pod['env'].append(
        {'name': 'SECRET_STORE_URL', 'value': '{{workflow.parameters.secret_store_url}}'})
    config_pod['env'].append({'name': 'VERBOSE', 'value': '{{workflow.parameters.verbose}}'})
    config_pod['volumeMounts'] = []
    config_pod['volumeMounts'].append({'name': 'workdir', 'mountPath': '/data'})
    config_pod['volumeMounts'].append({'name': 'artifacts-volume', 'mountPath': '/artifacts'})
    return config_pod


def create_execute_container(ddo):
    # setup nevermined
    options = {
        "resources": {
            "metadata.url": "http://172.17.0.1:5000",
        }
    }
    config = Config(options_dict=options)
    nevermined = Nevermined(config)
    workflow = ddo.metadata["main"]["workflow"]

    # TODO: Currently this only supports one stage
    transformation_did = workflow["stages"][0]["transformation"]["id"]
    transformation_ddo = nevermined.assets.resolve(transformation_did)
    transformation_metadata = transformation_ddo.get_service("metadata")

    # get args and container
    args = transformation_metadata.main["algorithm"]["entrypoint"]
    image = transformation_metadata.main["algorithm"]["requirements"]["container"]["image"]
    tag = transformation_metadata.main["algorithm"]["requirements"]["container"]["tag"]

    transformation_pod = dict()
    transformation_pod['name'] = "transformationPod"
    transformation_pod['image'] = f"{image}:{tag}"
    transformation_pod['imagePullPolicy'] = 'IfNotPresent'
    transformation_pod['command'] = ["sh", "-cxe"]
    transformation_pod['args'] = [f'cd $NEVERMINED_TRANSFORMATIONS_PATH/*/; \
                                  {args}; \
                                   ls -lR /data/outputs/']
    transformation_pod['env'] = []
    transformation_pod['env'].append(
        {'name': 'VOLUME', 'value': '{{workflow.parameters.volume}}'})
    transformation_pod['env'].append(
        {'name': 'NEVERMINED_INPUTS_PATH', 'value': '{{workflow.parameters.volume}}/inputs'})
    transformation_pod['env'].append(
        {'name': 'NEVERMINED_OUTPUTS_PATH', 'value': '{{workflow.parameters.volume}}/outputs'})
    transformation_pod['env'].append(
        {'name': 'NEVERMINED_TRANSFORMATIONS_PATH', 'value': '{{workflow.parameters.volume}}/transformations'})
    transformation_pod['volumeMounts'] = []
    transformation_pod['volumeMounts'].append({'name': 'workdir', 'mountPath': '/data'})
    return transformation_pod


def create_execute_coordinator():
    coordinator_execution = get_coordinator_execution_template()

    transformation_pod = coordinator_execution["templates"][0]
    transformation_pod["container"]['env'] = []
    transformation_pod["container"]['env'].append(
        {'name': 'VOLUME', 'value': '{{workflow.parameters.volume}}'})
    transformation_pod["container"]['env'].append(
        {'name': 'NEVERMINED_INPUTS_PATH', 'value': '{{workflow.parameters.volume}}/inputs'})
    transformation_pod["container"]['env'].append(
        {'name': 'NEVERMINED_OUTPUTS_PATH', 'value': '{{workflow.parameters.volume}}/outputs'})
    transformation_pod["container"]['env'].append(
        {'name': 'NEVERMINED_TRANSFORMATIONS_PATH', 'value': '{{workflow.parameters.volume}}/transformations'})
    transformation_pod["container"]['volumeMounts'] = []
    transformation_pod["container"]['volumeMounts'].append({'name': 'workdir', 'mountPath': '/data'})
    return transformation_pod


def create_publishing_container():
    config_pod = dict()
    config_pod['name'] = 'publishingPod'
    config_pod['image'] = 'keykoio/nevermined-pod-publishing-py:latest'
    config_pod['imagePullPolicy'] = 'IfNotPresent'
    config_pod['command'] = ["sh", "-cxe"]
    config_pod['args'] = 'ls /'
    config_pod['args'] = ["cp -rv /artifacts ./artifacts;\
         ls -l; \
         pod-publishing \
         --workflow $WORKFLOW \
         --path $VOLUME \
         --credentials $CREDENTIALS \
         --password $PASSWORD \
         --node $NODE \
         --gateway-url $GATEWAY_URL \
         --metadata-url $METADATA_URL \
         --secretstore-url $SECRET_STORE_URL; \
         ls -lR /data"]
    config_pod['env'] = []
    config_pod['env'].append(
        {'name': 'CREDENTIALS', 'value': '{{workflow.parameters.credentials}}'})
    config_pod['env'].append(
        {'name': 'PASSWORD', 'value': '{{workflow.parameters.password}}'})
    config_pod['env'].append(
        {'name': 'INPUTS', 'value': '{{workflow.parameters.inputs}}'})
    config_pod['env'].append(
        {'name': 'TRANSFORMATIONS', 'value': '{{workflow.parameters.transformations}}'})
    config_pod['env'].append(
        {'name': 'VOLUME', 'value': '{{workflow.parameters.volume}}'})
    config_pod['env'].append({'name': 'NODE', 'value': '{{workflow.parameters.node}}'})
    config_pod['env'].append(
        {'name': 'WORKFLOW', 'value': '{{workflow.parameters.workflow}}'})
    config_pod['env'].append(
        {'name': 'METADATA_URL', 'value': '{{workflow.parameters.metadata_url}}'})
    config_pod['env'].append(
        {'name': 'GATEWAY_URL', 'value': '{{workflow.parameters.gateway_url}}'})
    config_pod['env'].append(
        {'name': 'SECRET_STORE_URL', 'value': '{{workflow.parameters.secret_store_url}}'})
    config_pod['volumeMounts'] = []
    config_pod['volumeMounts'].append({'name': 'workdir', 'mountPath': '/data'})
    config_pod['volumeMounts'].append({'name': 'artifacts-volume', 'mountPath': '/artifacts'})
    return config_pod


def get_provider_account():
    return get_account(0)


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


def get_coordinator_execution_template():
    """Returns the argo coordinator workflow template

    Returns:
        dict: argo coordinator workflow template

    """
    path = Path(__file__).parent / "coordinator-workflow.yaml"
    with path.open() as f:
        coordinator_execution_template = yaml.safe_load(f)

    return coordinator_execution_template
