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
import public

func_name = 'missing'

def get_params(cfg, section, params, logger):
    #缺测值
    rst = public.get_opt_float(cfg, section, 'miss_value')
    if rst is None:
        raise Exception('missing %s miss_value error' % section)

    params[FixParamTypes.Miss] = rst
    
'''
def run_func(params, logger):
    dt = params[FixParamTypes.DT]
    nlon = params[FixParamTypes.NLon]
    nlat = params[FixParamTypes.NLat]
    slon = params[FixParamTypes.SLon]
    slat = params[FixParamTypes.SLat]
    elon = params[FixParamTypes.ELon]
    elat = params[FixParamTypes.ELat]
    dlon = params[FixParamTypes.DLon]
    dlat = params[FixParamTypes.DLat]
    level = params[FixParamTypes.Level] if FixParamTypes.Level in params else 0
    seq = params[FixParamTypes.SeqNum] if FixParamTypes.SeqNum in params else None
    miss_value = params[FixParamTypes.Miss] if FixParamTypes.Miss in params else 9999.0
    data_name = params[FixParamTypes.DName] if FixParamTypes.DName in params else 'data0'
    scale_decimals = params[FixParamTypes.ScaleDecimals] if FixParamTypes.ScaleDecimals in params else 2

    return public.get_grid_miss(dt, nlon, nlat, slon, slat, elon, elat, dlon, dlat,
                                level=level, seq=seq, miss_value=miss_value,
                                data_name = data_name, scale_decimals=scale_decimals)
'''

if __name__ == '__main__':
    print('done')
