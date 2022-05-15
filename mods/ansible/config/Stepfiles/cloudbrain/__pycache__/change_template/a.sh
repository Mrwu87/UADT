#! /bin/bash
for i in `ls | grep gotmpl`
do
	sed -i "s/10.0.10.147:31150/harbor.uisee.cn/g" $i
done


