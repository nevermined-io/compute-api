import os

from contracts_lib_py.utils import get_account


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
    arguments['parameters'].append({'name': 'node', 'value': 'http://192.168.178.21:8545'})
    arguments['parameters'].append({'name': 'verbose', 'value': 'false'})
    arguments['parameters'].append({'name': 'workflow', 'value': ddo.asset_id})
    arguments['parameters'].append(
        {'name': 'did_input_1', 'value': workflow['stages'][0]['input'][0]['id']})
    arguments['parameters'].append(
        {'name': 'did_input_2', 'value': workflow['stages'][0]['input'][1]['id']})
    arguments['parameters'].append(
        {'name': 'transformation_did', 'value': workflow['stages'][0]['transformation']['id']})
    # arguments['parameters'].append({'name': 'metadata_url', 'value': workflow['stages'][0][
    # 'output']['metadataUrl']})
    arguments['parameters'].append({'name': 'metadata_url', 'value': 'http://192.168.178.21:5000'})
    arguments['parameters'].append({'name': 'gateway_url', 'value': 'http://192.168.178.21:8030'})
    # arguments['parameters'].append({'name': 'gateway_url', 'value': workflow['stages'][0][
    # 'output']['accessProxyUrl']})
    arguments['parameters'].append(
        {'name': 'secret_store_url', 'value': 'http://192.168.178.21:12001'})
    # arguments['parameters'].append({'name': 'secret_store_url', 'value': workflow['stages'][0][
    # 'output']['secretStoreUrl']})
    return arguments


def create_volume_claim_templates():
    voloume_dict = [dict()]
    voloume_dict[0]['metadata'] = dict()
    voloume_dict[0]['metadata']['name'] = 'workdir'
    voloume_dict[0]['spec'] = dict()
    voloume_dict[0]['spec']['accessModes'] = ["ReadWriteOnce"]
    voloume_dict[0]['spec']['resources'] = dict()
    voloume_dict[0]['spec']['resources']['requests'] = dict()
    voloume_dict[0]['spec']['resources']['requests']['storage'] = '2Gi'
    return voloume_dict


def create_templates():
    templates = [dict()]
    templates[0]['name'] = 'compute-workflow'
    templates[0]['steps'] = []
    templates[0]['steps'].append([{'name': 'configurator', 'template': 'configuratorPod'}])
    # templates[0]['steps'].append([{'name': 'transformation', 'template': 'wordcountPod'}])
    # templates[0]['steps'].append([{'name': 'publishing', 'template': 'publishingPod'}])
    # templates.append({'name': 'configuratorPod', 'container': create_hello_container()})
    templates.append({'name': 'configuratorPod', 'container': create_configuration_container()})
    # templates.append({'name': 'wordcountPod', 'container': create_execute_container('wordcount')})
    # templates.append({'name': 'publishingPod', 'container': create_publishing_container()})
    return templates


def create_configuration_container():
    config_pod = dict()
    config_pod['name'] = 'configuratorPod'
    config_pod['image'] = 'keykoio/nevermined-pod-config'
    config_pod['command'] = ['sh', '-c']
    # config_pod['args'] = ["tail -f /dev/null"]
    config_pod['args'] = ["cp /artifacts/* /node_modules/@keyko-io/nevermined-contracts/artifacts/;\
         mkdir $VOLUME/adminlogs/; \
         node src/index.js \
         --workflow $WORKFLOW \
         --path $VOLUME \
         --credentials $CREDENTIALS \
         --password $PASSWORD \
         --node $NODE \
         --gateway-url $GATEWAY_URL \
         --verbose 2>&1 | tee $VOLUME/adminlogs/configure.log"]
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
    config_pod['env'].append({'name': 'WORKFLOW', 'value': '{{workflow.parameters.workflow}}'})
    config_pod['env'].append(
        {'name': 'GATEWAY_URL', 'value': '{{workflow.parameters.gateway_url}}'})
    config_pod['env'].append({'name': 'VERBOSE', 'value': '{{workflow.parameters.verbose}}'})
    config_pod['volumeMounts'] = []
    config_pod['volumeMounts'].append({'name': 'workdir', 'mountPath': '/data'})
    config_pod['volumeMounts'].append({'name': 'artifacts-volume', 'mountPath': '/artifacts'})
    return config_pod


def create_hello_container():
    config_pod = dict()
    config_pod['name'] = 'configuratorPod'
    config_pod['image'] = 'docker/whalesay:latest'
    config_pod['command'] = ['cowsay']
    config_pod['args'] = ['whalesay']
    # config_pod['args'] = """|
    #      node src/index.js \
    #      --workflow "$WORKFLOW" \
    #      --path "$VOLUME" \
    #      --workflowid "$WORKFLOWID" \
    #      --verbose 2>&1 | tee $VOLUME/adminlogs/configure.log"""
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
    config_pod['volumeMounts'] = []
    config_pod['volumeMounts'].append({'name': 'workdir', 'mountPath': '/data'})
    return config_pod


def create_execute_container(workflow_image):
    config_pod = dict()
    config_pod['name'] = workflow_image
    config_pod['image'] = workflow_image
    config_pod['command'] = ["sh", "-c"]
    config_pod['args'] = 'ls /'
    # config_pod['args'] = """|
    #      mkdir -p $VOLUME/outputs $VOLUME/logs
    #      java \
    #      -jar $VOLUME/transformations/$TRANSFORMATION_DID/wordCount.jar\
    #      --input1 $VOLUME/inputs/$DID_INPUT1/\
    #      --input2 $VOLUME/inputs/$DID_INPUT2/\
    #      --output $VOLUME/outputs/\
    #      --logs $VOLUME/logs/ | tee $VOLUME/logs/algorithm.log"""
    config_pod['env'] = []
    config_pod['env'].append(
        {'name': 'VOLUME', 'value': '{{workflow.parameters.volume}}'})
    config_pod['env'].append(
        {'name': 'DID_INPUT1', 'value': '{{workflow.parameters.did_input_1}}'})
    config_pod['env'].append(
        {'name': 'DID_INPUT2', 'value': '{{workflow.parameters.did_input_2}}'})
    config_pod['env'].append(
        {'name': 'TRANSFORMATION_DID', 'value': '{{workflow.parameters.transformation_did}}'})
    config_pod['volumeMounts'] = []
    config_pod['volumeMounts'].append({'name': 'workdir', 'mountPath': '/data'})
    return config_pod


def create_publishing_container():
    config_pod = dict()
    config_pod['name'] = 'publishingPod'
    config_pod['image'] = 'keykoio/nevermined-pod-publishing:latest'
    config_pod['command'] = ["sh", "-c"]
    config_pod['args'] = 'ls /'
    # config_pod['args'] = """|
    #      mkdir -p $VOLUME/outputs $VOLUME/logs
    #      node src/index.js \
    #      --workflow "$WORKFLOW" \
    #      --node "$NODE" \
    #      --credentials "$CREDENTIALS" \
    #      --password "$PASSWORD" \
    #      --path "$VOLUME" \
    #      --verbose | tee $VOLUME/logs/publish.log"""
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
        {'name': 'AWS_ACCESS_KEY_ID', 'value': '{{workflow.parameters.aws_access_key_id}}'})
    config_pod['env'].append(
        {'name': 'AWS_SECRET_ACCESS_KEY', 'value': '{{workflow.parameters.aws_secret_access_key}}'})
    config_pod['env'].append(
        {'name': 'METADATA_URL', 'value': '{{workflow.parameters.metadata_url}}'})
    config_pod['env'].append(
        {'name': 'GATEWAY_URL', 'value': '{{workflow.parameters.gateway_url}}'})
    config_pod['env'].append(
        {'name': 'SECRET_STORE_URL', 'value': '{{workflow.parameters.secret_store_url}}'})
    config_pod['volumeMounts'] = []
    config_pod['volumeMounts'].append({'name': 'workdir', 'mountPath': '/data'})
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
