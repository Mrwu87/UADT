#! /bin/bash
set -x
set -e
name=$1
ip=$2
passwd=$3



if [ -f "$HOME/.ssh/id_rsa.pub" ]; then

  cp ~/.ssh/id_rsa* mods/services/config/
  expect mods/services/config/sh/ssh-copy-id.exp  $name $ip  $passwd
else
  ssh-keygen  -P '' -f ~/.ssh/id_rsa
  if [ "$?" -eq "0" ]; then
    cp ~/.ssh/id_rsa* mods/services/config/
    expect mods/services/config/sh/ssh-copy-id.exp  $name $ip  $passwd
  else
    echo "keygen error" > mods/services/config/sshcopycheck/sshcopyfail.log
  fi
fi


