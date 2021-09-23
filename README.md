# Distributed port scanner
Works on kubernetes cluster

Architecture Diagram

<img src="/docs/images/architecture.png" alt="Architecture Diagram" width="600"/>

You can use it with Kubernetes cluster or docker-composer.

For using on Kubernetes, execute start_all.sh scripts under deployment/ folder.
It is going to use docker image on public docker hub.
Application will be ready on http://kubernetes-master-ip:30001

For using it with docker-compose
run "docker-compose up" command in /app folder.


Default credentials: admin/admin
