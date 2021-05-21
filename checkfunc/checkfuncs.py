#!/usr/bin/python
# -*- coding: utf-8 -*-
#Filename: checkfuncs.py

"""
Created on May 13, 2021

@author: anduin
"""

import checkfunc.func_diff_value_num as checkfunc_diff_value_num

def get_func_params(funcname, cfg, section, params):
    if funcname == checkfunc_diff_value_num.func_name:
        checkfunc_diff_value_num.get_params(cfg, section, params)
    else:
        raise Exception('unknown function name')

def run_func(funcname, params):
    if funcname == checkfunc_diff_value_num.func_name:
        checkfunc_diff_value_num.run_func(params)
    else:
        raise Exception('unknown function name')

if __name__ == '__main__':
    print('done')
