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
import spam.ansirunner
from threading import Thread


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

        if args.askpass:
            self.password = getpass.getpass("Password: ")
            #self.password = password.replace(" ", "")
            #self.password = "".join(password.split())
            #print "password:", self.password, "."
            if self.password == "lab":
                print "lab is printed"

        self.username = getpass.getuser()

        self.host_list = args.remote_hosts
        self.runner = spam.ansirunner.AnsibleRunner()
        os.environ["ANSIBLE_HOST_KEY_CHECKING"] = "False"
        self.check_host_connectivity()

    def check_host_connectivity(self):
        '''
        Check connectivity to all the remote hosts.
        '''
        result, _ = self.runner.ansible_perform_operation(
            host_list=self.host_list,
            remote_user=self.username,
            remote_pass=self.password,
            module="ping")

        print "[",
        for host in result['dark'].keys():
            print "%s: %s, " % (host, "fail"),

        for host in result['contacted'].keys():
            print "%s: %s, " % (host, "ok"),
        print "]\n"

    def exec_local_operation(self):
        '''
        Perform a local operation
        '''

    def exec_remote_operation(self):
        '''
        Remote operations on hosts
        '''
        cmd = ""

        while True:
            waiter = WaitIndicator()
            cmd = raw_input("> ")

            if cmd in ['quit', 'Quit', 'exit']:
                break

            if cmd.startswith("local:"):
                self.exec_local_operation()

            if len(cmd) <= 0:
                continue

            os.environ["ANSIBLE_HOST_KEY_CHECKING"] = "False"
            waiter.start()
            result, _ = self.runner.ansible_perform_operation(
                host_list=self.host_list,
                remote_user=self.username,
                remote_pass=self.password,
                module="command",
                module_args=cmd)

            waiter.stop_waiting()
            waiter.join()
            #Display results.
            for host in result['contacted'].keys():
                print "%s:" % host
                print "-" * len(host)
                print result['contacted'][host]['stdout']
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
                        required=True,
                        help="Enter a list of hosts to run the commands on")
    parser.add_argument("--askpass",
                        help="Ansible operation will prompt for user password",
                        action="store_true")
    args = parser.parse_args()

    return args


def main():
    args = parse_arguments()

    if not args.remote_hosts:
        print "require to specify hosts"
        return

    rexec = RemoteExecutor(args)
    rexec.exec_remote_operation()



if __name__ == '__main__':
    main()
