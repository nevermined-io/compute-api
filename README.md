[![banner](https://raw.githubusercontent.com/keyko-io/assets/master/images/logo/nevermined_logo_1.png)](https://nevermined.io)

# Nevermined Compute API 

> Compute to the Data Infrastructure Orchestration Micro-service


Table of Contents
=================

   * [nevermined-compute-api](#nevermined-compute-api)
      * [About](#about)
      * [Getting Started](#getting-started)
         * [Local Environment](#local-environment)
            * [Setting up minikube ](#setting-up-minikube)
            * [Running the Service](#running-the-service)
         * [Testing](#testing)
         * [New Version](#new-version)
      * [License](#license)



## About

The Compute API is a micro-service implementing the Nevermined Compute to the Data use case, 
in charge of managing the workflow executing requests.
Typically the Compute Service is integrated with the [Nevermined Gateway](https://github.com/keyko-io/nevermined-gateway),
but can be called independently of it.

The Compute API is in charge of establishing the communication with the K8s cluster, allowing to:

* Register workflows as K8s objects
* List the workflows registered in K8s
* Stop a running workflow execution
* Get information about the state of execution of a workflow

The Compute API doesn't provide any storage capability for workflows, all the state is stored directly in the K8s cluster.

## Getting Started

### Local Environment

The Compute API is in charge of receiving the requests for running compute workflows and the 
setup of those in the K8s infrastructure.
To do that, in a local environment the Compute API needs connectivity to you K8s environment.

There are multiple configurations and deployments of K8s possible, but here we are going to show 
how to connect to an existing K8s cluster running in minikube.

#### Setting up minikube

First is necessary to configure the `minikube` compute stack using
[`nevermined-tools`](https://github.com/keyko-io/nevermined-tools)

```bash
# There are some bugs affecting minikube with k8s 1.18.0 so we need to use 1.17.0
$ minikube config set kubernetes-version 1.17.0

# Start compute stack
$ ./scripts/setup_minikube.sh

# If minikube refuses to start due to virtualization problems be can set the minikube driver to docker
$ MINIKUBE_DRIVER=docker ./scripts/setup_minikube.sh

# Create a configmap for the artifacts
$ kubectl create configmap artifacts \
    --from-file=$HOME/.nevermined/nevermined-contracts/artifacts/ \
    --namespace=nevermined-compute

# Start the argo-artifacts service
$ helm install argo-artifacts stable/minio --set service.type=LoadBalancer \
    --set fullnameOverride=argo-artifacts

# If helm can't find argo-artifacts add the helm repo and try again
$ helm repo add stable https://kubernetes-charts.storage.googleapis.com/
$ helm repo update
```

#### Running the Service

Once you have the compute stack running with `minikube`, running the service is
as simple as running the following commands:

```bash
# Copy the artifacts
$ ./scripts/wait_for_migration_and_extract_keeper_artifacts.sh

# Set the environment variables
export FLASK_APP = nevermined_compute_api/run.py
export PROVIDER_ADDRESS=0x00bd138abd70e2f00903268f3db08f2d25677c9e
export PROVIDER_PASSWORD=node0
export PROVIDER_KEYFILE=tests/resources/data/publisher_key_file.json

# start the compute api
$ flask run --host=0.0.0.0 --port=8050
```

Having the server running you can find the complete Swagger API documentation
at [`http://localhost:8050/api/v1/docs/`](http://localhost:8050/api/v1/docs/)

### Testing

Automatic tests are set up via GitHub actions.

### New Version

The `bumpversion.sh` script helps bump the project version. You can execute the script using `{major|minor|patch}` 
as first argument, to bump the version accordingly.

## Attribution

This library service in the [Ocean Protocol](https://oceanprotocol.com) [Operator Service](https://github.com/oceanprotocol/operator-service).
It keeps the same Apache v2 License and adds some improvements. See [NOTICE file](NOTICE).

## License

```
Copyright 2020 Keyko GmbH
This product includes software developed at
BigchainDB GmbH and Ocean Protocol (https://www.oceanprotocol.com/)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```
