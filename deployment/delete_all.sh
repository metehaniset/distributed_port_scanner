#!/bin/bash
kubectl delete -f rabbitmq.yaml
kubectl delete -f elasticsearch.yaml
kubectl delete -f ps_worker.yaml
kubectl delete -f ps_result_manager.yaml
kubectl delete -f webui.yaml 

echo "----"
echo ""
kubectl get pods
