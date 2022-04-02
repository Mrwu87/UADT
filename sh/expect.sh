#!/bin/bash
name=$1
passwd=$2
ip=$3
new_ip=$4
gateway=$5
dns=$6
interface=$7
deploy_ip=$8
hostname=$9

if [ "$ip"   ==  "$deploy_ip" ]; then
  echo $passwd | sudo -S dpkg --list | grep -E  "^expect"
  if [ "$?"   -ne "0" ]; then
  echo $passwd | sudo -S dpkg -i initCheck/expectcheck/*.deb
  fi
fi
expect -version
if [ "$?"   -eq "0" ]; then
#echo "OK" && echo "$1"
#确保要有文件
  expect sh/sudo.exp $name $passwd $ip  $new_ip $gateway $dns $interface $hostname
    if [ "$?"   -ne  "0" ]; then
         echo  "expect change_ip Error!" >> initCheck/expectcheck/expectfail.log
   fi
else
  echo "expect install Error!" > initCheck/expectcheck/expectfail.log
fi



