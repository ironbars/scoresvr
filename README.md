scoresvr
========

A heavily over-engineered web application for serving musical scores.

Container Note
--------------

Now that this is containerized, you need to mount a volume with sheet music in  
it at `/app/scores` inside of the container.  Assuming you have a volume called  
`scorevol`:  

```
docker run -d -v scorevol:/app/scores -p 8080:8000 scoresvr:0.1.0
```
