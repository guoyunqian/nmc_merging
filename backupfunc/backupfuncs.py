#!/usr/bin/python
# -*- coding: utf-8 -*-
#Filename: checkfuncs.py

"""
Created on May 13, 2021

@author: anduin
"""

import backupfunc.func_forword as backupfunc_forword
import backupfunc.func_datasource as backupfunc_datasource
import backupfunc.func_missing as backupfunc_missing

def get_func_params(funcname, cfg, section, params, logger):
    if funcname == backupfunc_forword.func_name:
        backupfunc_forword.get_params(cfg, section, params, logger)
    elif funcname == backupfunc_datasource.func_name:
        backupfunc_datasource.get_params(cfg, section, params, logger)
    elif funcname == backupfunc_missing.func_name:
        backupfunc_missing.get_params(cfg, section, params, logger)
    else:
        raise Exception('unknown function name %s' % funcname)

'''
def run_func(funcname, params, logger):
    if funcname == backupfunc_forword.func_name:
        backupfunc_forword.run_func(params, logger)
    elif funcname == backupfunc_datasource.func_name:
        backupfunc_datasource.run_func(params, logger)
    elif funcname == backupfunc_missing.func_name:
        backupfunc_missing.run_func(params, logger)
    else:
        raise Exception('unknown function name %s' % funcname)
    '''
if __name__ == '__main__':
    print('done')
