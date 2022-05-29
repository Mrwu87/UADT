#!/bin/bash

NS=observability


# deploy fluentbit
kubectl apply -f $1/fluent-bit-configmap.yaml -n $NS
kubectl apply -f $1/fluent-bit-ds.yaml -n $NS