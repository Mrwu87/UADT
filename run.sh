#! /bin/bash
rm  -rf  mods/logs/config/runtime
#if [ `grep 'replicaCount' config/yaml/config.yaml | awk '{print $2}'` -eq 1 ];then
#  sed -i 's/replicaCount: "3"/replicaCount: "1"/g' mods/ansible/config/Stepfiles/openebs/cstor/cstor-sc.yaml
#else
#  sed -i 's/replicaCount: "1"/replicaCount: "3"/g' mods/ansible/config/Stepfiles/openebs/cstor/cstor-sc.yaml
#fi

if [ -d /usr/local/lib/python3.8/dist-packages/tailf-0.3.2-py3.8.egg ];then

  python3 main.py
else
  #sudo_passwd=`tail -n 10   ./config/yaml/config.yaml |  grep password  | awk '{print $2}'`
  sudo_passwd=`grep "password" ./config/yaml/config.yaml| tail -n 1 | awk '{print $2}'`
  cd mods/services/config/npyscreen
  tar -zxvf npyscreen-4.10.5.tar.gz
  cd npyscreen-4.10.5/
  echo $sudo_passwd | sudo -S python3 setup.py install
  cd ..
  tar -zxvf tailf-0.3.2.tar.gz
  cd  tailf-0.3.2
  echo $sudo_passwd | sudo -S python3 setup.py install
  cd ../../../../..
  python3 main.py
fi
