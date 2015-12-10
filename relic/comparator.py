#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Simple module to run commands remotely.
'''

import rex
from prettytable import PrettyTable
import textwrap


class Comparator(object):
    '''
    Comparator class.
    '''
    def __init__(self):

        '''
        Initialize comparator.
        '''

    def compare(self, **kwargs):
        '''
        Compare operation. Main function
        '''
        # Set the suggested type for dataset.
        # This could be different, we will reset this
        # flag if that is the case.
        dataset_type = kwargs.get('type', 'ini')

        datalist = kwargs.get('datalist', None)
        if not datalist:
            return

        results = []
        header = []
        fields = set()
        header.append("key")
        for dataset in datalist:
            result = {}
            result['node'] = dataset['node']
            header.append(dataset['node'])
            dataset['rexout'] = rex.parse_lrvalue_string(dataset['output'],
                                                         delimiter="=")
            # If the dataset is not a L <delim> R value,
            # then the result will be empty {}, in that case
            # save it as text only.

            if not dataset['rexout']:
                dataset['rexout'] = dataset['output']

            result['data'] = dataset['rexout']
            results.append(result)

            if isinstance(dataset['rexout'], dict):
                dataset_type = 'dict'
            elif isinstance(dataset['rexout'], str):
                dataset_type = 'str'

            if dataset_type == 'dict':
                for key in dataset['rexout']:
                    fields.add(key)

        x = PrettyTable(header)
        x.align["key"] = "l"
        for result in results:
            x.align[result['node']] = "l"

        if dataset_type == 'dict':
            for val in fields:
                row = []
                row.append(val)
                for result in results:
                    if val in result['data'].keys():
                        data_str = textwrap.fill(result['data'][val].strip(),
                                                 width=20)
                        row.append(data_str)
                    else:
                        row.append("None")
                x.add_row(row)
        elif dataset_type == 'str':
            row = []
            row.append("NA")
            for result in results:
                data_str = textwrap.fill(result['data'].strip(),
                                         width=20)
                row.append(data_str)

            x.add_row(row)

        print x


def main():
    print "main"



if __name__ == '__main__':
    main()
