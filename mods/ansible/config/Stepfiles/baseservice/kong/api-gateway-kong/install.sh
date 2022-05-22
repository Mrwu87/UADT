#!/bin/bash

NS=api-gateway-kong-new
ENV=common

# create namespace
kubectl create namespace $NS

# create kong-mtls secret
kubectl apply -f $1/api-gateway-kong/kong/secret-kong-mtls.yaml

# update helm repo
helm repo update

# deploy kong & konga
helmfile -f $1/api-gateway-kong/helmfile.yaml -e $ENV -n $NS  apply --skip-deps