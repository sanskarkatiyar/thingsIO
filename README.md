# thingsIO

## Instructions to run
Set up your cloud cluster. For GKE, this looks like:
```
gcloud config set compute/zone us-central1-b
gcloud container clusters create --preemptible tio
```
Clone this repository from Github:
```
git clone https://github.com/sanskarkatiyar/thingsIO
```
For a local Kubernetes cluster, you will need to enable port-forwarding. Execute `./deploy-local-dev.sh`.

For a cloud Kubernetes cluster, execute `./deploy-cloud-dev.sh`.
