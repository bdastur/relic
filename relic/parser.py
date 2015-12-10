#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
The Parser parses output usually ini file output from
multiple hosts, or output from CLI operations.
'''

import rex
from prettytable import PrettyTable
import textwrap
#import pprint


class Parser(object):
    '''
    Parser class - To parse results from remote hosts.
    '''
    def __init__(self):

        '''
        Initialize comparator.
        '''

    def parse_dataset(self, **kwargs):
        '''
        parse the dataset which can be results from multiple
        hosts and return a dictionary of parsed results.
        '''
        dataset = kwargs.get('datalist', None)

        results = {}
        for data in dataset:
            result = {}
            node_data = rex.parse_lrvalue_string(data['output'],
                                                 delimiter="=")
            # If the data is not a L<delim>R value, then
            # the result will be an empty {} dict. In that case
            # save it as text only.

            if not node_data:
                result['data'] = data['output']
                result['data_type'] = "str"
            else:
                result['data'] = node_data
                result['data_type'] = "dict"
            results[data['node']] = result

        return results

    def display_tabular(self, **kwargs):
        '''
        Compare operation. Main function
        '''
        datalist = kwargs.get('datalist', None)
        if not datalist:
            return

        newresults = self.parse_dataset(**kwargs)

        fields = set()
        for node in newresults.keys():
            print "node: ", node
            nodeobj = newresults[node]
            if nodeobj['data_type'] == 'dict':
                for key in nodeobj['data'].keys():
                    fields.add(key)

        header = []
        header.append("Key")
        for node in newresults.keys():
            header.append(node)

        x = PrettyTable(header)
        x.align["key"] = "l"
        for node in newresults.keys():
            x.align[node] = "l"

        if fields:
            for val in fields:
                row = []
                row.append(val)
                for node in newresults.keys():
                    nodeobj = newresults[node]
                    if val in nodeobj['data'].keys():
                        data_str = textwrap.fill(nodeobj['data'][val].strip(),
                                                 width=20)
                        row.append(data_str)
                    else:
                        row.append("None")
                x.add_row(row)
        else:
            row = []
            row.append("NA")
            for node in newresults.keys():
                nodeobj = newresults[node]
                data_str = textwrap.fill(nodeobj['data'].strip(),
                                         width=20)
                row.append(data_str)
            x.add_row(row)

        print x


def main():
    print "main"



if __name__ == '__main__':
    main()
