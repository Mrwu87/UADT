#!/bin/bash
IPADDR=$1
PORT=$2


result=`echo -e "\n" | telnet $IPADDR $PORT 2>/dev/null | grep Connected | wc -l`

if [ $result -eq 0 ]; then

      echo "$IPADDR $PORT is Closed." >> initCheck/portcheck/ssh_fail.log

fi
