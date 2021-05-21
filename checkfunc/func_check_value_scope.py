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

from publictype.fixparamtypes import FixParamTypes

func_name = 'check_value_scope'

def get_params(cfg, section, params):
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
    
    srccfg[FixParamTypes.CfgFilePath] = rst

def run_func(params):
    pass

if __name__ == '__main__':
    print('done')
