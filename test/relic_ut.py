#!/usr/bin/env python
# -*- coding: utf-8 -*-


import unittest
import relic.comparator


class RELICUT(unittest.TestCase):
    def test_basic(self):
        print "basic test"
        comparator = relic.comparator.Comparator()

        kwargs = {}
        kwargs['type'] = 'ini'
        kwargs['datalist'] = []
        node = {}
        node['node'] = "test.com"
        node['output'] = '''
        #Test comment


        field1innodb_additional_mem_pool_size=24M
        innodb_log_buffer_size=12M
        innodb_log_file_size=224M
        innodb_buffer_pool_size=4G
        '''
        kwargs['datalist'].append(node)

        node = {}
        node['node'] = "foo.com"
        node['output'] = '''
        innodb_additional_mem_pool_size=24M
        innodb_log_buffer_size=14M
        innodb_log_file_size=223M
        innodb_buffer_pool_size=4G
        wsrep_slave_threads=2
        wsrep_provider=/usr/lib64/libgalera_smm.so
        wsrep_cluster_address=gcomm://192.120.96.201,192.12096.205,192.120.96.28
        wsrep_node_name=v-osdb-001-prod
        wsrep_node_address=192.120.96.201
        '''
        kwargs['datalist'].append(node)

        comparator.compare(**kwargs)

    def test_simple_string(self):
        print "simple string"
        comparator = relic.comparator.Comparator()

        kwargs = {}
        kwargs['type'] = 'text'
        kwargs['datalist'] = []

        node = {}
        node['node'] = 'test.com'
        node['output'] = "this is a test"
        kwargs['datalist'].append(node)

        node = {}
        node['node'] = 'foo.com'
        node['output'] = """
        This is another test\n
        A multiline test"""

        kwargs['datalist'].append(node)

        comparator.compare(**kwargs)









