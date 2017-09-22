
(c) Copyright 2015-2016 Hewlett Packard Enterprise Development LP
(c) Copyright 2017 SUSE LLC

Licensed under the Apache License, Version 2.0 (the "License"); you may
not use this file except in compliance with the License. You may obtain
a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations
under the License.


README
======
percona-deploy.yml - deploys percona cluster.
percona-start.yml  - starts percona services, if all services down on all nodes percona-bootstrap
                     will need to be run.
percona-stop.yml   - stops percona .  If run on ALL nodes a manual bootstrap will need to be run.
percona-bootstrap.yml - Starts percona when all cluster nodes are down
percona-reconfigure.yml - Reconfigures Percona when a config change is made
percona-upgrade.yml - Upgrades Percona to a new version
percona-status.yml - Reports on the status of Percona Services
