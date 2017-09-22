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

serverid=$1
ipaddr=$2
role=$3
servergroup=$4
macaddr=$5
iloip=$6
clustername=$7
# adds a server entry into servers.yml based on provided args
cat <<EOF >> ~/openstack/my_cloud/definition/data/servers.yml
    - id: $serverid
      ip-addr: $ipaddr
      role: $role
      server-group: $servergroup
      mac-addr: $macaddr
      nic-mapping: VAGRANT
      ilo-ip: $iloip
      ilo-password: password
      ilo-user: admin
EOF

controlplane=~/openstack/my_cloud/definition/data/control_plane.yml
# get the member-count in cluster $7
membercount=$(grep -nA 10 "$clustername" $controlplane | awk '/member-count:/{print}' | cut -d ':' -f2 | xargs)
# get the linenumber of member count
linenum=$(grep -nA 10 "$clustername" $controlplane | awk '/member-count:/{print}' | cut -f1 -d"-")
# increase member-count by 1 in cluster $7
sed -i ''$linenum's/member-count: '$membercount'/member-count: '$((membercount + 1))'/' $controlplane
# add server role to control plane - get linenum of server role
serverrole=$(grep -nA 10 "$clustername" $controlplane | awk '/server-role:/{print}' | cut -f1 -d"-")
sed -i ''$serverrole' a\
            - '$role'' $controlplane
