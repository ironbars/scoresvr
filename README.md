# scoresvr

A heavily over-engineered web application for serving musical scores.

## Container Note

Now that this is containerized, you need to mount a volume with sheet music in  
it at `/app/scores` inside of the container.  Assuming you have a volume called  
`scores`:  

```
docker run -d -v scores:/app/scores -p 8080:8000 scoresvr:0.1.0
```

## Docker Compose

The compose file assumes that you have: 

1. An image with httpd configured to connect to the app (see the `web/`
   directory)
1. A Docker volume called `scores` created (see "Container Note" above)
1. A custom network called `scoresvr-net` created.  Alternatively, you could
   remove the `external` key and let Docker create it for you.

Lastly, you may need to rebuild the `scoresvr-httpd` image.  Edit the file
`web/scoresvr-httpd.conf` and uncomment the line:  

```
ProxyPass "/" "http://scoreserver:8000/"
```

After that rebuild the image like so:  

```
cd web/
docker build -t scoresvr-httpd .
```

## Kubernetes (minikube)

You'll need to rebuild the images so that minikube can use them.  See
[here](#building-the-images-for-minkube).

The `scoresvr.yaml` file assumes that you have mounted a directory containing
sheet music inside of minikube at `/scores`.

You can do that via:  

```
minikube mount /path/to/music:/scores
```

The process spawned by that command will have to stay active for as long as you
want the directory mounted.  See [this
page](https://minikube.sigs.k8s.io/docs/handbook/mount/) for more information.

You'll also need to create the service (TODO: add the service to the manifest).
Use:  

```
kubectl expose deployment/scoreserver --type=NodePort --port=8080
```

Lastly, you may need to rebuild the `scoresvr-httpd` image.  Edit the file
`web/scoresvr-httpd.conf` and uncomment the line:  

```
ProxyPass "/" "http://localhost:8000"
```

After that, rebuild the image as detailed in the [building
section](#building-the-images-for-minikube).

### Building the images for minikube

To allow minikube to use locally built Docker images, you need to do the
following in each shell that you want to build in:  

```
eval $(minikube -p minikube docker-env)
docker build -t <image_tag> .  # for example
```

Then you can issue the `docker build` command however you like.

