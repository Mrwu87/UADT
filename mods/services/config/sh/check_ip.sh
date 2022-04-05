
#!/bin/bash


ping -c1 -w1 -t5 $1 >/dev/null 2>&1
if [ "$?"   -ne  "0" ]; then
#echo "OK" && echo "$1"
 echo "$1" >> mods/services/config/ipcheck/ipLastfail.log
fi


  ##!/bin/bash
#  #echo -en "Pinging $1..."
#  rm -rf ipcheck/ipLastfail.log
#  touch ipcheck/ipLastfail.log
#  ping -c1 -w1 -t5 $1 >/dev/null 2>&1
#  if [ "$?"   -ne  "0" ]; then
#  #echo "OK" && echo "$1"
#   echo "$1" >> ipcheck/ipLastfail.log
#  fi