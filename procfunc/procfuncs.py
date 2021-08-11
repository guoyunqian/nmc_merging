#!/usr/bin/python
# -*- coding: utf-8 -*-
#Filename: procfuncs.py

"""
Created on May 13, 2021

@author: anduin
"""

import procfunc.func_select as procfunc_select
import procfunc.func_select_uv as procfunc_select_uv
import procfunc.func_max as procfunc_max
import procfunc.func_min as procfunc_min
import procfunc.func_cleansing_dstdata_with_nextseq as procfunc_cleansing_dstdata_with_nextseq

def get_func_params(funcname, cfg, section, params, logger):
    if funcname == procfunc_select.func_name:
        procfunc_select.get_params(cfg, section, params, logger)
    elif funcname == procfunc_max.func_name:
        procfunc_max.get_params(cfg, section, params, logger)
    elif funcname == procfunc_min.func_name:
        procfunc_min.get_params(cfg, section, params, logger)
    elif funcname == procfunc_select_uv.func_name:
        procfunc_select_uv.get_params(cfg, section, params, logger)
    elif funcname == procfunc_cleansing_dstdata_with_nextseq.func_name:
        procfunc_cleansing_dstdata_with_nextseq.get_params(cfg, section, params, logger)
    else:
        raise Exception('unknown function name %s' % funcname)

def set_func_params(funcname, save_dt, func_params, src_datas, savecfginfos, dst_datas, logger):
    if funcname == procfunc_select.func_name:
        return procfunc_select.set_func_params(save_dt, func_params, src_datas, savecfginfos, dst_datas, logger)
    elif funcname == procfunc_max.func_name:
        return procfunc_max.set_func_params(save_dt, func_params, src_datas, savecfginfos, dst_datas, logger)
    elif funcname == procfunc_min.func_name:
        return procfunc_min.set_func_params(save_dt, func_params, src_datas, savecfginfos, dst_datas, logger)
    elif funcname == procfunc_select_uv.func_name:
        return procfunc_select_uv.set_func_params(save_dt, func_params, src_datas, savecfginfos, dst_datas, logger)
    elif funcname == procfunc_cleansing_dstdata_with_nextseq.func_name:
        return procfunc_cleansing_dstdata_with_nextseq.set_func_params(save_dt, func_params, src_datas, savecfginfos, dst_datas, logger)
    else:
        raise Exception('unknown function name %s' % funcname)

def run_func(funcname, params, logger):
    if funcname == procfunc_select.func_name:
        procfunc_select.run_func(params, logger)
    elif funcname == procfunc_max.func_name:
        procfunc_max.run_func(params, logger)
    elif funcname == procfunc_min.func_name:
        procfunc_min.run_func(params, logger)
    elif funcname == procfunc_select_uv.func_name:
        procfunc_select_uv.run_func(params, logger)
    elif funcname == procfunc_cleansing_dstdata_with_nextseq.func_name:
        procfunc_cleansing_dstdata_with_nextseq.run_func(params, logger)
    else:
        raise Exception('unknown function name %s' % funcname)

if __name__ == '__main__':
    print('done')
