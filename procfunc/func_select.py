#!/usr/bin/python
# -*- coding: utf-8 -*-
#Filename: func_select.py

"""
Created on May 13, 2021

@author: anduin
"""

import public
from publictype.fixparamtypes import FixParamTypes

func_name = 'select'

#读select函数需要的参数
def get_params(cfg, section, params, logger):
    #处理过程需要用到的数据集合
    rst = public.get_opt_str(cfg, section, 'data')
    if rst is None or len(rst) == 0:
        raise Exception('select %s data error' % section)

    params[FixParamTypes.DatasName] = rst

    #对应时效没有数据时如何处理
    rst = public.get_opt_float(cfg, section, 'miss_value')
    if rst is None:
        raise Exception('select %s miss_value error' % section)
        
    params[FixParamTypes.Miss] = rst

    #对应结果的时效
    rst = public.get_opt_str(cfg, section, 'seq')
    if rst is None:
        raise Exception('select %s seq error' % section)
        
    seq = public.parse_list(rst, is_num=True, right_c=True)
    if len(seq) == 0:
        seq = None

    params[FixParamTypes.SeqObj] = seq

#设置运行参数
def set_func_params(save_dt, func_params, src_datas, savecfginfos, dst_datas, logger):
    params = {}
    params[FixParamTypes.GridDataList] = src_datas[func_params[FixParamTypes.DatasName]]
    params[FixParamTypes.DstGridData] = dst_datas
    params[FixParamTypes.DT] = save_dt

    params[FixParamTypes.NLon] = savecfginfos[FixParamTypes.NLon]
    params[FixParamTypes.NLat] = savecfginfos[FixParamTypes.NLat]
    params[FixParamTypes.SLon] = savecfginfos[FixParamTypes.SLon]
    params[FixParamTypes.SLat] = savecfginfos[FixParamTypes.SLat]
    params[FixParamTypes.ELon] = savecfginfos[FixParamTypes.ELon]
    params[FixParamTypes.ELat] = savecfginfos[FixParamTypes.ELat]
    params[FixParamTypes.DLon] = savecfginfos[FixParamTypes.DLon]
    params[FixParamTypes.DLat] = savecfginfos[FixParamTypes.DLat]

    params[FixParamTypes.SeqObj] = func_params[FixParamTypes.SeqObj]
    params[FixParamTypes.Miss] = func_params[FixParamTypes.Miss]

    params[FixParamTypes.ScaleDecimals] = savecfginfos[FixParamTypes.ScaleDecimals]

    return params

#select数据
def run_func(params, logger):
    datas = params[FixParamTypes.GridDataList]
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
    seq = params[FixParamTypes.SeqObj] if FixParamTypes.SeqObj in params else None
    miss_value = params[FixParamTypes.Miss] if FixParamTypes.Miss in params else 9999.0
    data_name = params[FixParamTypes.DName] if FixParamTypes.DName in params else 'data0'
    scale_decimals = params[FixParamTypes.ScaleDecimals] if FixParamTypes.ScaleDecimals in params else 2

    dst_datas = params[FixParamTypes.DstGridData]

    for s in seq:
        if s in datas:
            dst_datas[s] = datas[s]
        else:
            dst_datas[s] = public.get_grid_missing(dt, nlon, nlat, slon, slat, elon, elat, dlon, dlat, level=level, seq=s, \
                miss_value=miss_value, data_name = data_name, scale_decimals=scale_decimals)

if __name__ == '__main__':
    print('done')
