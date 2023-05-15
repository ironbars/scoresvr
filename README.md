scoresvr
========

A heavily over-engineered web application for serving musical scores.

Container Note
--------------

Now that this is containerized, you need to mount a volume with sheet music in  
it at `/app/scores` inside of the container.  Assuming you have a volume called  
`scores`:  

```
docker run -d -v scores:/app/scores -p 8080:8000 scoresvr:0.1.0
```

Docker Compose
--------------

The compose file assumes that you have: 

1. An image with httpd configured to connect to the app (see the `web/`
   directory)
1. A Docker volume called `scores` created (see "Container Note" above)
1. A custom network called `scoresvr-net` created.  Alternatively, you could
   remove the `external` key and let Docker create it for you.

Kubernetes (minikube)
---------------------

The `scoresvr.yaml` file assumes that you have mounted a directory containing
sheet music inside of minikube at `/scores`.

You can do that via:  

```
minikube mount /path/to/music:/scores
```

The process spawned by that command will have to stay active for as long as you
want the directory mounted.  See [this
page](https://minikube.sigs.k8s.io/docs/handbook/mount/) for more information.
