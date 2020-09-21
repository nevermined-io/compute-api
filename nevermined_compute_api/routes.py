import logging
import json
import requests
from configparser import ConfigParser
from os import path

import kubernetes
import yaml
from argo.workflows import config
from argo.workflows.client import V1alpha1Api
from flask import Blueprint, jsonify, request
from kubernetes.client.rest import ApiException
from kubernetes import client, config as kubernetes_config
from nevermined_sdk_py import Nevermined, Config

from nevermined_compute_api.workflow_utils import setup_keeper, create_execution

services = Blueprint('services', __name__)

# Configuration to connect to k8s.
if not path.exists('/.dockerenv'):
    config.load_kube_config()
    kubernetes_config.load_kube_config()
else:
    config.load_incluster_config()
    kubernetes_config.load_incluster_config()

# create instance of the API class
v1alpha1 = V1alpha1Api()
# create instance of the kubernetes client
kubernetes_client = client.CoreV1Api()

config_parser = ConfigParser()
configuration = config_parser.read('config.ini')
group = config_parser.get('resources', 'group')  # str | The custom resource's group name
version = config_parser.get('resources', 'version')  # str | The custom resource's version
namespace = config_parser.get('resources', 'namespace')  # str | The custom resource's namespace

setup_keeper()

@services.route('/init', methods=['POST'])
def init_execution():
    """
    Initialize the execution when someone call to the execute endpoint in brizo.
    swagger_from_file: docs/init.yml
    """
    body = create_execution(request.json["serviceAgreementId"], request.json['workflow'])

    try:
        api_response = v1alpha1.create_namespaced_workflow(namespace, body)
        logging.info(api_response)
        return api_response.metadata.name, 200

    except ApiException as e:
        logging.error(
            f'Exception when calling V1alpha1Api->create_namespaced_workflow: {e}')
        return 'Workflow could not start', 400


@services.route('/stop/<execution_id>', methods=['DELETE'])
def stop_execution(execution_id):
    """
    Stop the current workflow execution.
    swagger_from_file: docs/stop.yml
    """
    name = execution_id  # str | the custom object's name
    body = kubernetes.client.V1DeleteOptions()  # V1DeleteOptions |
    grace_period_seconds = 56  # int | The duration in seconds before the object should be
    # deleted. Value must be non-negative integer. The value zero indicates delete immediately.
    # If this value is nil, the default grace period for the specified type will be used.
    # Defaults to a per object value if not specified. zero means delete immediately. (optional)
    orphan_dependents = True  # bool | Deprecated: please use the PropagationPolicy, this field
    # will be deprecated in 1.7. Should the dependent objects be orphaned. If true/false,
    # the \"orphan\" finalizer will be added to/removed from the object's finalizers list. Either
    # this field or PropagationPolicy may be set, but not both. (optional)
    propagation_policy = 'propagation_policy_example'  # str | Whether and how garbage collection
    # will be performed. Either this field or OrphanDependents may be set, but not both. The
    # default policy is decided by the existing finalizer set in the metadata.finalizers and the
    # resource-specific default policy. (optional)

    try:
        api_response = v1alpha1.delete_namespaced_workflow(namespace, name, body=body,
                                                           grace_period_seconds=grace_period_seconds,
                                                           orphan_dependents=orphan_dependents,
                                                           propagation_policy=propagation_policy)
        logging.info(api_response)
    except ApiException as e:
        print("Exception when calling CustomObjectsApi->delete_namespaced_custom_object: %s\n" % e)
    return 'Successfully delete', 200


@services.route('/info/<execution_id>', methods=['GET'])
def get_execution_info(execution_id):
    """
    Get info for an execution id.
    swagger_from_file: docs/execution_info.yml
    """
    try:
        api_response = v1alpha1.get_namespaced_workflow(namespace, execution_id)
        logging.info(api_response)
        return yaml.dump(api_response.metadata), 200
    except ApiException as e:
        logging.error(f'The executionId {execution_id} is not registered in your namespace.')
        return f'The executionId {execution_id} is not registered in your namespace.', 400


@services.route('/list', methods=['GET'])
def list_executions():
    """
    List all the execution workflows.
    swagger_from_file: docs/list_executions.yml
    """
    try:
        api_response = v1alpha1.list_namespaced_workflows(namespace)
        result = list()
        for i in api_response.items:
            result.append(i.metadata.name)
        logging.info(api_response)
        return jsonify(result), 200

    except ApiException as e:
        logging.error(
            f'Exception when calling CustomObjectsApi->list_cluster_custom_object: {e}')
        return 'Error listing workflows', 400


@services.route('/logs/<execution_id>', methods=['GET'])
def get_logs(execution_id):
    """
    Get the logs for an execution id.
    swagger_from_file: docs/logs.yml
    """
    try:
        api_workflow = v1alpha1.get_namespaced_workflow(namespace, execution_id)
    except ApiException as e:
        logging.error(f"Exception when calling v1alpha1.get_namespaced_workflow: {e}")
        return f'Error getting workflow {execution_id}', 400

    # the root node does not contain logs
    del api_workflow.status.nodes[execution_id]

    result = []
    for (node_id, status) in api_workflow.status.nodes.items():
        pod_name = status.display_name

        try:
            api_logs = kubernetes_client.read_namespaced_pod_log(name=node_id, namespace=namespace,
                                                                 container="main")
        except ApiException as e:
            if e.status == 404:
                # the pod is not running yet
                continue

            logging.error(f"Error getting pod {node_id} logs: {e}")
            return f"Error getting logs", 400

        for line in api_logs.split("\n"):
            result.append({"podName": pod_name, "content": line})

    return jsonify(result), 200


@services.route('/status/<execution_id>', methods=['GET'])
def get_status(execution_id):
    """
    Get the status for an execution id.
    swagger_from_file: docs/status.yml
    """
    try:
        api_workflow = v1alpha1.get_namespaced_workflow(namespace, execution_id)
    except ApiException as e:
        logging.error(f"Exception when calling v1alpha1.get_namespaced_workflow: {e}")
        return f'Error getting workflow {execution_id}', 400

    result = {}
    pods = []
    for (node_id, status) in api_workflow.status.nodes.items():
        pod_name = status.display_name
        if pod_name == execution_id:
            result = {
                "status": status.phase,
                "startedAt": status.started_at.isoformat(timespec="seconds") + "Z",
                "finishedAt": status.finished_at.isoformat(timespec="seconds") + "Z" \
                    if status.finished_at else None,
                "did": None,
                "pods": []
            }
        else:
            status_message = {
                "podName": pod_name,
                "status": status.phase,
                "startedAt": status.started_at.isoformat(timespec="seconds") + "Z",
                "finishedAt": status.finished_at.isoformat(timespec="seconds") + "Z" \
                    if status.finished_at else None,
            }
            pods.append(status_message)

    result["pods"] = pods

    if result["status"] == "Succeeded":
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
        ddo = nevermined.assets.search(f'"{execution_id}"')[0]
        result["did"] = ddo.did

    return jsonify(result), 200
