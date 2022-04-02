#!/bin/bash

ip=$1
deploy_ip=$2

if [ "$ip"   ==  "$deploy_ip" ]; then
  tar -xvf initCheck/ansiblecheck/pip-22.0.3.tar.gz -C  initCheck/ansiblecheck/
  cd initCheck/ansiblecheck/pip-22.0.3/
  sudo python3 setup.py install
  cd ..
  pip list | grep -E "ansible|prettytable"
  if [ "$?"   -ne "0" ]; then
      sudo pip install --no-index --find-links=.  prettytable
      sudo pip install --no-index --find-links=.  enlighten
      sudo tar -zxvf   ansible5.4.tar.gz
      sudo pip install --no-index --find-links=.  ansible
      result=`pip list | grep -E "ansible|prettytable" | wc -l`
      if [ $result   -lt 2 ]; then
          echo "Error install ansible and prettytable" > ansiblefail.log
      fi

  fi

fi