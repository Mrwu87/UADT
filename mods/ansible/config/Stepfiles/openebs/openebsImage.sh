#!/bin/bash
for i in $(ls  $2 | grep -E  "*.tar")
do
        sudo docker load -i $2$i

done
for i in `ls  $2  | grep -E  "*.tar" | awk -F .  '{print $1}'`
do
        if [ $i == "provisioner-localpv" ]; then
   sudo docker tag   openebs/$i:3.1.0   $1:31150/openebs/$i:3.1.0
   sudo docker push $1:31150/openebs/$i:3.1.0

        else
        sudo docker tag   openebs/$i:1.8.0   $1:31150/openebs/$i:1.8.0
        sudo docker push $1:31150/openebs/$i:1.8.0
        fi
done
