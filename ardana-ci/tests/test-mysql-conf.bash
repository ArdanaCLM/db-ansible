#!/bin/bash
#
# (c) Copyright 2016 Hewlett Packard Enterprise Development LP
# (c) Copyright 2017 SUSE LLC
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
# e.g
#    test-mysql-conf cp1 slow_query_log ON
# tests if slow_query_log is set ON on cp1 and
# NOT set ON elsewhere if this is run elsewhere
#  Currently only run on the deployer
set -vx
echo " $1 $2 $3"
cnfstatus=0
if [[ $(hostname) == *"$1"* ]]
then
  sudo mysql -e "show variables like '$2'" | grep $3
  if [[ $? == 1 ]]
  then
    cnfstatus=1
  fi
fi
if [[ $(hostname) != *"$1"* ]]
then
  sudo mysql -e "show variables like '$2'" | grep  $3
  if [[ $? == 0 ]]
  then
    cnfstatus=1
  fi
fi
exit $cnfstatus
