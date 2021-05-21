#!/usr/bin/python
# -*- coding: utf-8 -*-
#Filename: func_diff_value_num.py

"""
Created on May 13, 2021

@author: anduin
"""

import os
import shutil
import datetime

from publictype.fixparamtypes import FixParamTypes

func_name = 'diff_value_num'

def get_params(cfg, section, params):
    #数据场中不同数值的最小数目
    rst = public.get_opt_int(cfg, section, 'diff_num')
    if rst is None:
        raise Exception('diff_value_num %s diff_num error' % section)
        
    params[FixParamTypes.DiffNum] = rst


def run_func(params):
    grd = params[FixParamTypes.GridData]
    diff_num = params[FixParamTypes.DiffNum]

    return len(set(grd.values.flatten().tolist())) > diff_num

if __name__ == '__main__':
    print('done')
