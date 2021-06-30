#!/usr/bin/python
# -*- coding: utf-8 -*-
#Filename: func_max.py

"""
Created on May 13, 2021

@author: anduin
"""

import public
import numpy as np

from publictype.fixparamtypes import FixParamTypes

func_name = 'max'

#读max函数需要的参数
def get_params(cfg, section, params, logger):
    #处理过程需要用到的数据集合
    rst = public.get_opt_str(cfg, section, 'data')
    if rst is None or len(rst) == 0:
        raise Exception('max %s data error' % section)

    params[FixParamTypes.DatasName] = rst
    '''
    #处理过程需要用到的数据集合
    rst = public.get_opt_str(cfg, section, 'compare_data')
    if rst is None or len(rst) == 0:
        raise Exception('max %s compare_data error' % section)

    params[FixParamTypes.DatasNameC] = rst
    '''
    #数据中缺测值
    rst = public.get_opt_float(cfg, section, 'miss_value')
    #if rst is None:
    #    raise Exception('max %s miss_value error' % section)
        
    params[FixParamTypes.Miss] = rst
    
    #时效的间隔
    rst = public.get_opt_int(cfg, section, 'seq_delta')
    if rst is None:
        rst = 0
        
    params[FixParamTypes.SeqDelta] = rst

#设置运行参数
def set_func_params(save_dt, func_params, src_datas, savecfginfos, dst_datas, logger):
    params = {}
    params[FixParamTypes.GridDataList] = src_datas[func_params[FixParamTypes.DatasName]]
    params[FixParamTypes.DstGridData] = dst_datas

    params[FixParamTypes.Miss] = func_params[FixParamTypes.Miss]
    params[FixParamTypes.SeqDelta] = func_params[FixParamTypes.SeqDelta]

    return params

#比较并获得最大的数据
def run_func(params, logger):
    datas = params[FixParamTypes.GridDataList]
    miss_value = params[FixParamTypes.Miss] if FixParamTypes.Miss in params else None
    seqdelta = params[FixParamTypes.SeqDelta] if FixParamTypes.SeqDelta in params else 0

    dst_datas = params[FixParamTypes.DstGridData]

    for s in dst_datas.keys():
        for curseq in range(s - seqdelta, s+1):
            if curseq in datas.keys():
                dst_datas[s].values = np.fmax(datas[curseq].values, dst_datas[s].values)

if __name__ == '__main__':
    print('done')
