#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['preview'],
    'supported_by': 'SuSE'
}

DOCUMENTATION = '''
---
module: find_galera_mariadb_bootstrap_host

short_description: Figure out the best way to restart the cluster.

version_added: "1.9"

description:
    - This action module will analyse the result of service status,
      safe_to_bootstrap status, and seqno to determine the best way to
      restart the cluster. If all the nodes are down, it will figure out
      the node in which to bootstrap the cluster. If some of the nodes are
      down and some of them are still alive, it will simply return the list
      of nodes to restart or rejoin the cluster. This module does not work
      by itself. Rather, it is relying on the tasks to find the server
      status, safe_to_boostrap attribute, and seqno attribute from each of
      the cluster nodes. This module merely going over those results and
      determine the best way to restart the cluster.

options:
    hostvars:
        description:
            - Ansible hostvars dict
        required: true
    mdb_hosts:
        description:
            - List of hosts which make up the MariaDB cluster.
        required: true

extends_documentation_fragment:
    -

author:
    - Guang Yee (guang.yee@suse.com)
'''

EXAMPLES = '''
- name: FND-MDB | _suse_galera_bootstrap | Look for safe_to_bootstrap
  shell: >
    cat /var/lib/mysql/grastate.dat | grep safe_to_bootstrap |
    awk '{print $2}'
  register: safe_to_bootstrap_result

- name: FND-MDB | _suse_galera_bootstrap | Lookup seqno
  shell: >
    cat /var/lib/mysql/grastate.dat | grep seqno |
    awk '{print $2}'
  register: seqno_result

- name: FND-MDB | _suse_galera_bootstrap | Check if service is active (exited)
  become: yes
  shell: "systemctl status {{ mysql_service }}"
  register: mysql_service_result
  failed_when: false
  changed_when: '"active (exited)" in mysql_service_result.stdout'

- name: FND-MDB | _suse_galera_bootstrap | Find Galera MariaDB bootstrap host
  find_galera_mariadb_bootstrap_host:
    hostvars: "{{ hostvars }}"
  register: find_bootstrap_host_result

- name: FND-MDB | _suse_galera_bootstrap | Bootstrap host
  debug:
    msg: "Bootstrap HOst: {{ find_bootstrap_host_result.bootstrap_host }}"
  when: find_bootstrap_host_result.bootstrap_host is defined
'''

RETURN = '''
bootstrap_host:
    description: The inventory host where we should be bootstrapping the
                 cluster. This attribute is set only if all the nodes are down
                 and the bootstrap node is found. If one or more nodes in the
                 cluster are still alive, there's no need to perform the
                 bootstrap sequence. Therefore, this attribute will not be set.
    type: str
hosts_to_start:
    description: The list of inventory hosts to perform normal restart. This
                 attribute will always set. However, it may contain an empty
                 list if all the hosts in the cluster are still alive and well.
    type: list
'''

from ansible.module_utils.basic import *

def find_host_with_safe_to_bootstrap(hostvars, hosts):
    for host in hosts:
        if hostvars[host]['safe_to_bootstrap_result']['stdout'] == '1':
            return host


def find_host_with_highest_seqno(hostvars, hosts):
    highest_seqno = 0
    host_with_highest_seqno = None
    for host in hosts:
        seqno = int(hostvars[host]['seqno_result']['stdout'])
        if seqno > highest_seqno:
            highest_seqno = seqno
            host_with_highest_seqno = host
    return host_with_highest_seqno


def find_hosts_where_mysql_still_running(hostvars, hosts):
    alive_hosts = []
    for host in hosts:
        if int(hostvars[host]['mysql_service_status_result']['rc']) == 0:
            if int(hostvars[host]['mysql_process_status_result']['rc']) == 0:
                seqno = int(hostvars[host]['seqno_result']['stdout'])
                # If the mysql is running, the seqno should be -1.
                if seqno != -1:
                    raise Exception('Mysql appeared to be running on host %s, '
                                    'but the sequence number is not -1 as '
                                    'expected.', host)
                alive_hosts.append(host)
            else:
                # We have a FUBAR situation here. Systemd is reporting that
                # mysql service is alive, but the mysqld process is not found.
                # Human intervention is required.
                raise Exception('Systemd on host %s indicating mysql service '
                                'still alive. But the process mysqld is not '
                                'found.', host)
    return alive_hosts


def run_module():
    # define the available arguments/parameters that a user can pass to
    # the module
    module_args = dict(
        hostvars=dict(type='dict', required=True),
        mdb_hosts=dict(type='list', required=True)
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # change is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
        original_message='',
        message='',
        bootstrap_host=None,
        hosts_to_start=[]
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        return result

    # manipulate or modify the state as needed (this is going to be the
    # part where your module will do what it needs to do)
    hostvars = module.params.get("hostvars")
    hosts = module.params.get("mdb_hosts")

    try:
        alive_hosts = find_hosts_where_mysql_still_running(hostvars, hosts)
        if alive_hosts:
            dead_hosts = list(set(hosts) - set(alive_hosts))
            if dead_hosts:
                result['hosts_to_start'] = dead_hosts
        else:
            safe_to_bootstrap_host = find_host_with_safe_to_bootstrap(
                hostvars, hosts)
            if safe_to_bootstrap_host:
                result['bootstrap_host'] = safe_to_bootstrap_host
            else:
                highest_seqno_host = find_host_with_highest_seqno(
                    hostvars, hosts)
                if highest_seqno_host:
                    result['bootstrap_host'] = highest_seqno_host
                else:
                    raise Exception('Unable to determine a bootstrap host '
                                    'either safe_to_boostrap or seqno')
            result['hosts_to_start'] = list(
                set(hosts) - set([result['bootstrap_host']]))
    except Exception, e:
        module.fail_json(msg=e.message)
    else:
        module.exit_json(**result)


def main():
    run_module()

if __name__ == '__main__':
    main()
