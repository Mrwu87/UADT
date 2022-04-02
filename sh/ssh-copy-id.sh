#! /bin/bash
set -x
set -e
name=$1
ip=$2
passwd=$3

if [ -f "$HOME/.ssh/id_rsa.pub" ]; then

  cp ~/.ssh/id_rsa* .
  expect sh/ssh-copy-id.exp  $name $ip  $passwd
else
  ssh-keygen  -P '' -f ~/.ssh/id_rsa
  if [ "$?" -eq "0" ]; then
    cp ~/.ssh/id_rsa* .
    expect sh/ssh-copy-id.exp  $name $ip  $passwd
  else
    echo "keygen error" > initCheck/sshcopycheck/sshcopyfail.log
  fi
fi


