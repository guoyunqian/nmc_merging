#!/usr/bin/python
# -*- coding: utf-8 -*-
#Filename: procfuncs.py

"""
Created on May 13, 2021

@author: anduin
"""

import procfunc.func_select as procfunc_select

def get_func_params(funcname, cfg, section, params, logger):
    if funcname == procfunc_select.func_name:
        procfunc_select.get_params(cfg, section, params, logger)
    else:
        raise Exception('unknown function name %s' % funcname)

def set_func_params(funcname, save_dt, func_params, src_datas, savecfginfos, dst_datas, logger):
    if funcname == procfunc_select.func_name:
        return procfunc_select.set_func_params(save_dt, func_params, src_datas, savecfginfos, dst_datas, logger)
    else:
        raise Exception('unknown function name %s' % funcname)

def run_func(funcname, params, logger):
    if funcname == procfunc_select.func_name:
        procfunc_select.run_func(params, logger)
    else:
        raise Exception('unknown function name %s' % funcname)

if __name__ == '__main__':
    print('done')
