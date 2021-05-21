#!/usr/bin/python
# -*- coding: utf-8 -*-
#Filename: func_datasource.py

"""
Created on May 13, 2021

@author: anduin
"""

import os
import shutil
import datetime

from publictype.fixparamtypes import FixParamTypes

func_name = 'datasource'

def get_params(cfg, section, params):
    #配置ini
    rst = public.get_opt_str(cfg, section, 'src')
    if rst is None:
        raise Exception('datasource %s src error' % section)

    params[FixParamTypes.CfgFilePath] = rst

    #往回找的时间列表
    rst = public.get_opt_float(cfg, section, 'timedelta')
    if rst is None:
        raise Exception('datasource %s timedelta error' % section)

    deltas = public.parse_list(rst, is_num=True, right_c=True)

    params[FixParamTypes.Deltas] = deltas
    
'''
def run_func(params):
    pass
'''

if __name__ == '__main__':
    print('done')
