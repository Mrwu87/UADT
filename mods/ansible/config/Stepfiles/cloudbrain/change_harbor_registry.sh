#! /bin/bash
for i in `ls | grep gotmpl`
do
    sed -i "s/harbor.uisee.cn/$1/g" $i
    sed -i "s&cloud-js-qianxi.uisee.com&$2&g" $i
    if [ $i != 'app-console-operator-latest.yaml.gotmpl' ];then
       sed -i "s&dongwu.uisee.com&$2&g"  $i
    fi
    sed -i "s&jiashan.uisee.com&$2&g" $i
    sed -i "s&UcloudKubernetes&$3&g" $i
    if [ $i == 'cloud-nome-latest.yaml.gotmpl' ];then
       sed -i "s&local-Namespace&$4&g"  $i
    fi
    #sed -i "s&projectName: dongwu&projectName: $4&g" $i
    #jiashan-dongwu namespace
done

