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
poetry install --no-root # gives you pymongo
export SCORESVR_SCORES_DIR=/path/to/scores
poetry run python3 data/scores2json.py
```

You'll need a running instance of MongoDB for the rest.  I'd recommend spinning
up a kind cluster with a extra mount for the `/data/db` directory.  The you can
do the following:  

```
kubectl apply -f manifests/mongodb-nodeport-svc.yaml
# this defaults to localhost if undefined
export SCORESVR_MONGO_HOST="localhost"
# script uses the default mongo port of 27017 if undefined, so be sure to define
# this
export SCORESVR_MONGO_PORT=30017 
poetry run python3 data/import.py
```

Note that, with the `requirements.txt` file present, you don't really need
poetry for much beyond importing the scores.  If you are wanting to tinker and
end up adding another dependency, however, you will need it along with its
export plugin (which you will get with running `poetry install` at the root of
this repo).  Update the requirements file like so:  

```
poetry export -f requirements.txt -o requirements.txt
```

Then rebuild the image.

### Kubernetes (kind)

Before anything else, you'll need to create your cluster with 

* [extra mounts](https://kind.sigs.k8s.io/docs/user/configuration/#extra-mounts)
* settings for [ingress](https://kind.sigs.k8s.io/docs/user/ingress/)
* a [local registry](https://kind.sigs.k8s.io/docs/user/local-registry/)

Configurations can all be found [here](https://github.com/ironbars/kind-iron).

You'll need [docker](https://www.docker.com/) installed for this to work if
you're using this repository.  It's possible to do this with minikube as well,
but you'll need a different setup and workflow.

There is a script in that repo (`kind-with-registry.sh`) that will start up a
cluster with port mappings for ingress and a NodePort service to interact with
Mongo from outside of the cluster.  You'll just need to define your data
directory.

#### Automation with Task

You can use [task](https://github.com/go-task/task) to deploy the app once your
kind cluster is running.  The `build`, `push`, and `deploy` tasks all require
the local registry as described above.  The following commands will do it.  

Build the app image:  

```
task build
```

Push the image into your local registry:  

```
task push
```

Finally deploy the app:  

```
task init
```

Lastly, once the app is deployed, you can use the other configured tasks to make
changes.  After you've made a change, run the following to deploy:  

```
task deploy
```

You can change the `CLUSTER_NAME` and `NAMESPACE` variables at your preference,
as long as they match what you configured for your kind cluster.
