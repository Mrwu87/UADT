#!/bin/bash

ip=$1
deploy_ip=$2

if [ "$ip"   ==  "$deploy_ip" ]; then
  tar -xvf mods/services/config/ansiblecheck/pip-22.0.3.tar.gz -C  mods/services/config/ansiblecheck/
  cd mods/services/config/ansiblecheck/pip-22.0.3/
  sudo python3 setup.py install
  cd ..
  res=`pip list | grep -E "ansible|prettytable|enlighten" | wc -l`
  if [ $res   -lt 3 ]; then
      sudo pip install --no-index --find-links=.  prettytable
      sudo pip install --no-index --find-links=.  enlighten
      sudo tar -zxvf   ansible5.4.tar.gz
      sudo pip install --no-index --find-links=.  ansible

      result=`pip list | grep -E "ansible|prettytable|enlighten" | wc -l`
      if [ $result   -lt 3 ]; then
          echo "Error install ansible and prettytable" >  mods/services/config/ansiblecheck/ansiblefail.log
      else
        sudo bash -c " echo logger=logging.getLogger\(\'ansible_log\'\) >>  /usr/local/lib/python3.8/dist-packages/ansible/utils/display.py"
      fi
  else
        cat /usr/local/lib/python3.8/dist-packages/ansible/utils/display.py | grep "logger=logging.getLogger('ansible_log')"
        if [ $?  -ne 0 ]; then
           sudo bash -c " echo logger=logging.getLogger\(\'ansible_log\'\) >>  /usr/local/lib/python3.8/dist-packages/ansible/utils/display.py"
        else
          echo "Skip: display.py logger is Ready "
        fi

  fi

fi