#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Simple module to run commands remotely.
'''

import os
import sys
import time
import itertools
import argparse
import getpass
import pyansible.ansirunner
import pyansible.ansiInventory
from threading import Thread
import subprocess


class WaitIndicator(Thread):
    '''
    Wait indicator Thread.
    '''
    def __init__(self):
        super(WaitIndicator, self).__init__()
        self.done = False

    def run(self):
        time.sleep(2)
        for c in itertools.cycle(r"/-\|"):
            if self.done:
                break
            display = "[" + c + "]"
            sys.stdout.write(display)
            sys.stdout.write('\r')
            sys.stdout.flush()
            time.sleep(0.5)

    def stop_waiting(self):
        self.done = True


class RemoteExecutor(object):
    '''
    Remote Executor
    '''
    def __init__(self, args):
        '''
        Initialize the executor.
        '''

        if args.password:
            self.password = args.password
        elif args.askpass:
            self.password = getpass.getpass("Password: ")
        else:
            self.password = None

        if args.asksudopass:
            self.sudo_pass = getpass.getpass(
                "Sudo password [Default ssh password]")
            if len(self.sudo_pass) == 0:
                self.sudo_pass = self.password
            self.sudo = True
            self.sudo_user = 'root'
        else:
            self.sudo = False
            self.sudo_user = None
            self.sudo_pass = None

        self.username = getpass.getuser()

        if args.remote_hosts:
            self.host_list = args.remote_hosts
        else:
            self.host_list = None

        if args.group:
            self.host_group = args.group[0]
        else:
            self.host_group = "all"

        if args.inventory_file:
            self.inventory = pyansible.ansiInventory.AnsibleInventory(
                args.inventory_file[0])
            if not self.inventory.get_hosts(self.host_group):
                print "No hosts found for group %s" % self.host_group
                sys.exit()

            self.host_list = self.inventory.get_hosts(
                self.host_group)[0]['hostlist']

        self.runner = pyansible.ansirunner.AnsibleRunner()
        self.state = "remote"
        os.environ["ANSIBLE_HOST_KEY_CHECKING"] = "False"
        self.check_host_connectivity()

    def check_host_connectivity(self):
        '''
        Check connectivity to all the remote hosts.
        '''
        waiter = WaitIndicator()
        waiter.start()
        result, _ = self.runner.ansible_perform_operation(
            host_list=self.host_list,
            remote_user=self.username,
            remote_pass=self.password,
            module="ping")
        waiter.stop_waiting()
        waiter.join()

        print "[",
        for host in result['dark'].keys():
            print "%s: %s, " % (host, "fail"),

        for host in result['contacted'].keys():
            print "%s: %s, " % (host, "ok"),
        print "]\n"

    def exec_local_operation(self, cmd):
        '''
        Perform a local operation
        '''
        try:
            sproc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
            output = sproc.communicate()[0]
            print output
        except OSError as oserr:
            print "oserror: %s" % oserr

    def exec_adhoc_operation(self, cmd):
        '''
        A single operation on hosts,
        '''
        if cmd is None or len(cmd) == 0:
            print "cmd required."
            return
        os.environ["ANSIBLE_HOST_KEY_CHECKING"] = "False"

        result, _ = self.runner.ansible_perform_operation(
            host_list=self.host_list,
            remote_user=self.username,
            remote_pass=self.password,
            sudo=self.sudo,
            sudo_user=self.sudo_user,
            sudo_pass=self.sudo_pass,
            module="shell",
            module_args=cmd)

        #Display results.
        for host in result['contacted'].keys():
            print "%s:" % host
            print "-" * len(host)
            try:
                print result['contacted'][host]['stdout']
            except KeyError:
                print "No stdout"
            print "\n-- output end --\n"

    def exec_remote_operation(self):
        '''
        Remote operations on hosts
        '''
        cmd = ""

        while True:
            waiter = WaitIndicator()
            if self.state == "remote":
                cmd = raw_input("> ")
            elif self.state == "local":
                cmd = raw_input("local> ")

            if cmd in ['quit', 'Quit', 'exit']:
                if self.state == "local":
                    self.state = "remote"
                    continue
                else:
                    break

            if cmd.startswith("local:"):
                # Change state to local.
                self.state = "local"
                continue

            if self.state == "local":
                cmd = cmd.strip().split(" ")
                self.exec_local_operation(cmd)
                continue

            if len(cmd) <= 0:
                continue

            os.environ["ANSIBLE_HOST_KEY_CHECKING"] = "False"
            waiter.start()
            result, _ = self.runner.ansible_perform_operation(
                host_list=self.host_list,
                remote_user=self.username,
                remote_pass=self.password,
                sudo=self.sudo,
                sudo_user=self.sudo_user,
                sudo_pass=self.sudo_pass,
                module="shell",
                module_args=cmd)

            waiter.stop_waiting()
            waiter.join()
            #Display results.
            for host in result['contacted'].keys():
                print "%s:" % host
                print "-" * len(host)
                try:
                    print result['contacted'][host]['stdout']
                except KeyError:
                    print "No stdout"
                print "\n-- output end --\n"


def show_help():
    '''
    Display help
    '''
    description = """
    Remote operations made easy
    ----------------------------
    Example: remote_run.py -r contr-1.xyz.net 10.10.10.100
             > ls
    """

    return description


def parse_arguments():
    '''
    Parse the command line arguments.
    '''
    parser = argparse.ArgumentParser(
        prog="remote_run.py",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=show_help())
    parser.add_argument("-r", "--remote_hosts",
                        nargs='+',
                        required=False,
                        help="Enter a list of hosts to run the commands on")
    parser.add_argument("-i", "--inventory_file",
                        nargs='+',
                        required=False,
                        help="Enter the ansible inventory file")
    parser.add_argument("-g", "--group",
                        nargs='+',
                        required=False,
                        help="Enter the host group [default all]")
    parser.add_argument("--askpass",
                        help="Ansible operation will prompt for user password",
                        action="store_true")
    parser.add_argument("--asksudopass",
                        help="Ansible operation will prompt for sudo password",
                        action="store_true")
    parser.add_argument("--adhoc",
                        nargs='+',
                        required=False,
                        help="Run any adhoc command on remote host")
    parser.add_argument("--password",
                        required=False,
                        type=str,
                        help="Password for remote user (required if adhoc option is chosen).")

    args = parser.parse_args()

    if not args.remote_hosts and not args.inventory_file:
        print "Require either -r <host list> or -i <inventory file option"
        sys.exit()

    if args.inventory_file and \
            not os.path.exists(args.inventory_file[0]):
        print "%s not found. Invalid inventory file" % args.inventory_file[0]
        sys.exit()

    return args


def main():
    args = parse_arguments()

    if args.adhoc is not None:
        if args.password is None:
            print "password required for adhoc operation"
            sys.exit()
        # With password option, --askpass and --akssudopass are not needed.
        args.askpass = args.asksudopass = None
   
    rexec = RemoteExecutor(args) 
    if args.adhoc is not None:
        cmd = " ".join(args.adhoc)
        rexec.exec_adhoc_operation(cmd)
    else:
        rexec.exec_remote_operation()



if __name__ == '__main__':
    main()

