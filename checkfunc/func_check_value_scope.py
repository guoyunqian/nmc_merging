#!/usr/bin/python
# -*- coding: utf-8 -*-
#Filename: func_check_value_scope.py

"""
Created on May 13, 2021

@author: anduin
"""

import os
import shutil
import datetime

import public
from publictype.fixparamtypes import FixParamTypes

func_name = 'check_value_scope'

def get_params(cfg, section, params, logger):
    #有效值的最小值
    rst = public.get_opt_float(cfg, section, 'min_value')
    if rst is None:
        raise Exception('check_value_scope %s min_value error' % section)
        
    params[FixParamTypes.MinValue] = rst
    
    #有效值的最大值
    rst = public.get_opt_float(cfg, section, 'max_value')
    if rst is None:
        raise Exception('check_value_scope %s max_value error' % section)
        
    params[FixParamTypes.MaxValue] = rst
    
    #数据源配置文件
    rst = public.get_opt_str(cfg, section, 'replace_src')
    if rst is None:
        raise Exception('check_value_scope %s replace_src error' % section)
    
    params[FixParamTypes.CfgFilePath] = rst
    
def set_params(params, grd, checkcfg, logger):
    params[FixParamTypes.GridData] = grd
    params[FixParamTypes.MinValue] = checkcfg[FixParamTypes.MinValue]
    params[FixParamTypes.MaxValue] = checkcfg[FixParamTypes.MaxValue]
    params[FixParamTypes.CfgFilePath] = checkcfg[CfgFilePath]

def run_func(params, logger):
    return True

if __name__ == '__main__':
    print('done')
