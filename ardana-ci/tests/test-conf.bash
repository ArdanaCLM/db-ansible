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
#  test-conf cp1 value my.cnf
#  tests to see if value is in my.cnf on cp1 and not in my.cnf
#  on any other control plane
set -vx
echo " $1 $2 $3"
cnfstatus=0
if [[ $(hostname) == *"$1"* ]]
then
  sudo grep  "$2" "$3"
  if [[ $? == 1 ]]
  then
    cnfstatus=1
  fi
fi
if [[ $(hostname) != *"$1"* ]]
then
  sudo grep  "$2" "$3"
  if [[ $? == 0 ]]
  then
    cnfstatus=1
  fi
fi
exit $cnfstatus


