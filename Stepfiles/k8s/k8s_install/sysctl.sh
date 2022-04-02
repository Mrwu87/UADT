sudo echo """
hard nofile 65535
soft nofile 65535
""" >>  /etc/security/limits.conf
sudo  echo """
vm.swappiness = 0
net.bridge.bridge-nf-call-iptables = 1
net.ipv4.conf.all.rp_filter = 1
net.ipv4.ip_forward = 1
net.bridge.bridge-nf-call-ip6tables = 1
""" > /etc/sysctl.conf
sudo  sysctl -p
sudo  swapoff -a
sudo cp /etc/fstab /etc/fstab_bak
sudo cat /etc/fstab_bak | grep -v swap > /etc/fstab