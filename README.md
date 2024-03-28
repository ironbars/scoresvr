# scoresvr

A heavily over-engineered web application for serving musical scores.

## Deployment

### Prerequisites

For the scores, this repository relies on
[https://github.com/ironbars/scores](https://github.com/ironbars/scores).  

You can run the `build.sh` script from there to generate the PDFs (requires
[lilypond](https://lilypond.org/)).  

Run the following to get JSON representations of the score metadata and the
engravings (requires [poetry](https://python-poetry.org)):

```
poetry install # gives you pymongo
export SCORESVR_SCORES_DIR=/path/to/scores
poetry run python3 data/scores2json.py
```

You'll need a running instance of MongoDB for the rest.  I'd recommend spinning
up a kind cluster with a extra mount for the `/data/db` directory.  The you can
do the following:  

```
# this defaults to localhost if undefined
export SCORESVR_MONGO_HOST="mongo.url"
# this is the default port; script uses this if this variable is undefined
export SCORESVR_MONGO_PORT=27017 
poetry run python3 data/import.py
```

### Kubernetes (kind)

Before anything else, you'll need to create your cluster with [extra
mounts](https://kind.sigs.k8s.io/docs/user/configuration/#extra-mounts) and
settings for [ingress](https://kind.sigs.k8s.io/docs/user/ingress/).  The
configurations can all be found [here](https://github.com/ironbars/kind-iron).

#### Automation with Task

You can use [task](https://github.com/go-task/task) to deploy the app once your
kind cluster is running.  The following commands will do it.  

Build the images:  

```
task build-all
```

Load the images into your cluster:  

```
task load-all
```

Finally deploy the app:  

```
task init-app
```

Lastly, once the app is deployed, you can use the other configured tasks to make
changes.  After you've made a change, run the following to deploy:  

```
task deploy
```

You can change the `CLUSTER_NAME` and `NAMESPACE` variables at your preference,
as long as they match what you configured for your kind cluster.

### Kubernetes (minikube)

You'll need to rebuild the images so that minikube can use them.  See
[here](#building-the-images-for-minkube).

You'll also need to mount a directory for Mongo.  See [this
page](https://minikube.sigs.k8s.io/docs/handbook/mount/) for instructions.

Lastly, enable ingress:

```
minikube addons enable ingress
```

#### Building the images for minikube

To allow minikube to use locally built Docker images, you need to do the
following in each shell that you want to build in:  

```
eval $(minikube -p minikube docker-env)
docker build -t <image_tag> .  # for example
```

Then you can issue the `docker build` command however you like.

#### Deploying the app

```
kubectl create namespace scoreserver
kubectl apply -f manifests/{service,scoreserver,ingress}.yaml -n scoreserver
```
