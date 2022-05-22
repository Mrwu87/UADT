#!/bin/bash

NS=kube-public
ENV=mini

helm repo update
# deploy storage minio-s3
helmfile -f $1/helmfile.yaml -e $ENV -n $NS apply --skip-deps