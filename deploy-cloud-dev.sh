#!/bin/sh

kubectl apply -f redis/redis-deployment.yaml
kubectl apply -f redis/redis-service.yaml
kubectl apply -f rabbitmq/rabbitmq-deployment.yaml
kubectl apply -f rabbitmq/rabbitmq-service.yaml
kubectl apply -f influxdb/influxdb-deployment.yaml
kubectl apply -f influxdb/influxdb-service.yaml
kubectl apply -f dashboard/dashboard-deployment.yaml
kubectl apply -f dashboard/dashboard-service.yaml
kubectl apply -f rest/rest-deployment.yaml
kubectl apply -f rest/rest-service.yaml
kubectl apply -f analytics/analytics-deployment.yaml
kubectl apply -f ingestor/ingestor-deployment.yaml
kubectl apply -f rest/rest-ingress.yaml