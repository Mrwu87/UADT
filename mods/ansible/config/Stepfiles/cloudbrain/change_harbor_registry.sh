#! /bin/bash
for i in `ls | grep gotmpl`
do
	sed -i "s/harbor.uisee.cn/$1/g" $i
done

