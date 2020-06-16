def create_arguments():
    arguments = dict()
    arguments['parameters'] = []
    arguments['parameters'].append({'name': 'credentials', 'value': 'fulanito'})
    arguments['parameters'].append({'name': 'password', 'value': 'xxx'})
    arguments['parameters'].append({'name': 'inputs', 'value': '/data/input_folder'})
    arguments['parameters'].append(
        {'name': 'transformations', 'value': '/data/transformations_folder'})
    arguments['parameters'].append({'name': 'volume', 'value': ' /data'})
    arguments['parameters'].append({'name': 'node', 'value': 'keeper_url'})
    arguments['parameters'].append({'name': 'workflow', 'value': 'nombre_workflow'})
    arguments['parameters'].append({'name': 'did_input_1', 'value': 'did:nv:xxxxx'})
    arguments['parameters'].append({'name': 'did_input_2', 'value': 'did:nv:xxxxx'})
    arguments['parameters'].append({'name': 'transformation_did', 'value': 'did:nv:xxxxx'})
    arguments['parameters'].append({'name': 'aws_access_key_id', 'value': 'xxxxx'})
    arguments['parameters'].append({'name': 'aws_secret_access_key', 'value': 'xxxxx'})
    arguments['parameters'].append({'name': 'metadata_url', 'value': 'metadata:5000'})
    arguments['parameters'].append({'name': 'gateway_url', 'value': 'gateway:8030'})
    arguments['parameters'].append({'name': 'secret_store_url', 'value': 'secret_store:12001'})
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
    templates[0]['steps'].append([{'name': 'transformation', 'template': 'wordcountPod'}])
    templates[0]['steps'].append([{'name': 'publishing', 'template': 'publishingPod'}])
    templates.append({'name': 'configuratorPod', 'container': create_configuration_container()})
    templates.append({'name': 'wordcountPod', 'container': create_execute_container('wordcount')})
    templates.append({'name': 'publishingPod', 'container': create_publishing_container()})
    return templates


def create_configuration_container():
    config_pod = dict()
    config_pod['name'] = 'nevermined-pod-config'
    config_pod['image'] = 'keykoio/nevermined-pod-config:latest'
    config_pod['command'] = "[sh, -c]"
    config_pod['args'] = """|
         node src/index.js \
         --workflow "$WORKFLOW" \
         --path "$VOLUME" \
         --workflowid "$WORKFLOWID" \
         --verbose 2>&1 | tee $VOLUME/adminlogs/configure.log"""
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
    config_pod['command'] = "[sh, -c]"
    config_pod['args'] = """|
         mkdir -p $VOLUME/outputs $VOLUME/logs
         java \
         -jar $VOLUME/transformations/$TRANSFORMATION_DID/wordCount.jar\
         --input1 $VOLUME/inputs/$DID_INPUT1/\
         --input2 $VOLUME/inputs/$DID_INPUT2/\
         --output $VOLUME/outputs/\
         --logs $VOLUME/logs/ | tee $VOLUME/logs/algorithm.log"""
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
    config_pod['name'] = 'nevermined-pod-publishing'
    config_pod['image'] = 'keykoio/nevermined-pod-publishing:latest'
    config_pod['command'] = "[sh, -c]"
    config_pod['args'] = """|
         mkdir -p $VOLUME/outputs $VOLUME/logs
         node src/index.js \
         --workflow "$WORKFLOW" \
         --node "$NODE" \
         --credentials "$CREDENTIALS" \
         --password "$PASSWORD" \
         --path "$VOLUME" \
         --verbose | tee $VOLUME/logs/publish.log"""
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