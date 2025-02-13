# scoresvr

A heavily over-engineered web application for serving musical scores.

## Deployment

### Prerequisites

For the scores, this repository relies on
[https://github.com/ironbars/scores](https://github.com/ironbars/scores).  

You can run the `build.sh` script from there to generate the PDFs (requires
[lilypond](https://lilypond.org/)).  

You'll need [docker](https://www.docker.com/) installed for this to work if
you're using this repository.  It's possible to do this with minikube as well,
but you'll need a different setup and workflow.

### Kubernetes (kind)

Before anything else, you'll need to create your cluster with 

* [extra mounts](https://kind.sigs.k8s.io/docs/user/configuration/#extra-mounts)
* settings for [ingress](https://kind.sigs.k8s.io/docs/user/ingress/)
* a [local registry](https://kind.sigs.k8s.io/docs/user/local-registry/)

Configurations for kind can all be found
[here](https://github.com/ironbars/kind-iron).

There is a script in that repo (`kind-with-registry.sh`) that will start up a
cluster with port mappings for ingress and a NodePort service to interact with
Mongo from outside of the cluster.  The necessary mounts will also be present.
You'll just need to edit the location of your data directory.

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

### Data Ingestion

To ingest the score data, you'll need to either:

1. Expose the MongoDB instance running in your newly created cluster
2. Run MongoDB outside of the cluster, but point it at the same data directory
   you're using inside of the cluster.

I've created a `NodePort` service to deal with option 1:  

```
kubectl apply -f manifests/mongodb-nodeport-svc.yaml
```

You'll either need [poetry](https://python-poetry.org/) or to use `venv` and
`pip` to create an virtual environment (this doc only deals with poetry).

```
poetry install --no-root # gives you pymongo
```

Then you can run the following to populate the database:  

```
poetry run data/ingest /path/to/a/score

# OR

poetry run data/ingest -d /path/to/many/scores
```
### Miscellaneous

Note that, with the `requirements.txt` file present, you don't really need
poetry for much beyond importing the scores.  If you are wanting to tinker and
end up adding another dependency, however, you will need it along with its
export plugin (which you will get with running `poetry install` at the root of
this repo).  Update the requirements file like so:  

```
poetry export -f requirements.txt -o requirements.txt
```

Then rebuild the app image.


