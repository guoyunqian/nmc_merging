#!/usr/bin/python
# -*- coding: utf-8 -*-
#Filename: checkfuncs.py

"""
Created on May 13, 2021

@author: anduin
"""

import checkfunc.func_diff_value_num as checkfunc_diff_value_num
import checkfunc.func_check_value_scope as checkfunc_check_value_scope

def get_func_params(funcname, cfg, section, params, logger):
    if funcname == checkfunc_diff_value_num.func_name:
        checkfunc_diff_value_num.get_params(cfg, section, params, logger)
    elif funcname == checkfunc_check_value_scope.func_name:
        checkfunc_check_value_scope.get_params(cfg, section, params, logger)
    else:
        raise Exception('unknown function name %s' % funcname)
    
def set_func_params(funcname, params, grd, checkcfg, logger):
    if funcname == checkfunc_diff_value_num.func_name:
        checkfunc_diff_value_num.set_params(params, grd, checkcfg, logger)
    elif funcname == checkfunc_check_value_scope.func_name:
        checkfunc_check_value_scope.set_params(params, grd, checkcfg, logger)
    else:
        raise Exception('unknown function name %s' % funcname)

def run_func(funcname, params, logger):
    if funcname == checkfunc_diff_value_num.func_name:
        checkfunc_diff_value_num.run_func(params, logger)
    elif funcname == checkfunc_check_value_scope.func_name:
        checkfunc_check_value_scope.run_func(params, logger)
    else:
        raise Exception('unknown function name %s' % funcname)

if __name__ == '__main__':
    print('done')
