#!/bin/bash
set -vx
version=`dpkg -l | grep percona-xtradb-cluster-common | awk '{print $3}'`

if [[ $version == $1 ]]
then
  upgradestatus=0
else
  upgradestatus=1
fi
exit $upgradestatus
