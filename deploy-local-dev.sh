#!/bin/sh

# To kill the port-forward processes use "ps augxww | grep port-forward"
# to identify the processes ids and then "kill -9 <pid>"

kubectl apply -f redis/redis-deployment.yaml
kubectl apply -f redis/redis-service.yaml
kubectl apply -f rabbitmq/rabbitmq-deployment.yaml
kubectl apply -f rabbitmq/rabbitmq-service.yaml

# kubectl port-forward --address 0.0.0.0 service/rabbitmq 5672:5672 &
# kubectl port-forward --address 0.0.0.0 service/redis 6379:6379