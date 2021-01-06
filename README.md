# thingsIO

## Design Documentation and Demo

### Document

You can find our detailed design and documentation [here in this PDF file](docs/5253_report.pdf).

### Youtube video

Link: https://youtu.be/oSRw8uqio6g

<a href="http://www.youtube.com/watch?feature=player_embedded&v=oSRw8uqio6g
" target="_blank"><img src="http://img.youtube.com/vi/oSRw8uqio6g/0.jpg" 
alt="thingsIO: Youtube video" width="640" height="480" border="1" /></a>



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
