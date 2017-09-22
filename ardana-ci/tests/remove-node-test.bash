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
server_name=$1
serverrole=$2
clustername=$3
controlplane=~/openstack/my_cloud/definition/data/control_plane.yml
# remove server $1 from servers.yml
sed -i '/id: '$server_name'/,+9d' ~/openstack/my_cloud/definition/data/servers.yml
# remove server role from control plane
sed -i '/'$serverrole'/d' $controlplane
# get member count from control plane
membercount=$(grep -nA 10 "$clustername" $controlplane | awk '/member-count:/{print}' | cut -d ':' -f2 | xargs)
# get line number of member-count
linenum=$(grep -nA 10 "$clustername" $controlplane | awk '/member-count:/{print}' | cut -f1 -d"-")
# reduce member-count by 1
sed -i ''$linenum's/member-count: '$membercount'/member-count: '$((membercount - 1))'/' $controlplane
