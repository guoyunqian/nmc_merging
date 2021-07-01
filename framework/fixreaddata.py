#!/usr/bin/python
# -*- coding: utf-8 -*-
#Filename: fixreaddata.py

'''
Created on Aug 21, 2020

@author: anduin
'''

import os
import numpy as np
import json
import datetime
import pandas as pd
import xarray
import time

from publictype.fixparamtypes import FixParamTypes

class FixReadData(object):
    def __init__(self, logger):
        self.logger = logger
        
    #处理grib的过滤条件,filters的格式为：产品分类 产品编号 层次类型 层次值，其中不需要的条件设置为-1
    #grib2文件中对应的变量名：parameterCategory parameterNumber typeOfFirstFixedSurface level
    def __filter_grib_msg(self, grb, filters):
        if filters is None:
            return True

        splitrsts = filters.split()
        if len(splitrsts) != 4:
            raise Exception('filters format error %s' % str(filters))

        rst = int(splitrsts[0])
        if rst >= 0 and grb.parameterCategory != rst:
            return False
        
        rst = int(splitrsts[1])
        if rst >= 0 and grb.parameterNumber != rst:
            return False

        rst = int(splitrsts[2])
        if rst >= 0 and grb.typeOfFirstFixedSurface != rst:
            return False

        rst = int(splitrsts[3])
        if rst >= 0 and grb.level != rst:
            return False

        return True

    #读单个grib2文件，返回以seqnum为key，文件中grib为value的字典
    def read_gribdata_from_grib2_with_pygrib_single_file_seqnum(self, params):
        from publictype.gribtypes import GribTypes
        
        from_file = params[FixParamTypes.SFullPath]
        seq_key_is_num = params[FixParamTypes.SeqKeyIsNum] if FixParamTypes.SeqKeyIsNum in params else False
        seq_and_p_num = None
        if FixParamTypes.SeqAndPNum in params:
            seq_and_p_num = params[FixParamTypes.SeqAndPNum]
        elif FixParamTypes.SeqObj in params:
            if seq_key_is_num:
                seq_and_p_num = params[FixParamTypes.SeqObj]
            else:
                seq_and_p_num = list(map(str, params[FixParamTypes.SeqObj]))

        #seqfield = params[FixParamTypes.SeqField] if FixParamTypes.SeqField in params else GribTypes.endStep
        pnumfield = params[FixParamTypes.PNumField] if FixParamTypes.PNumField in params else None   #GribTypes.perturbationNumber
        
        logger = params[FixParamTypes.CurLogger] if FixParamTypes.CurLogger in params else None
        if logger is None:
            logger = self.logger

        filters = params[FixParamTypes.Filters] if FixParamTypes.Filters in params else None

        try:
            import pygrib
            logger.info('FixReadData read_gribdata_from_grib2_with_pygrib_single_file_seqnum start %s' % (str(params)))
            
            rst = {}
            grbs = pygrib.open(from_file)
            for grb in grbs:
                if not self.__filter_grib_msg(grb, filters):
                    continue

                seqnum = 0
                if grb.productDefinitionTemplateNumber == 0:
                    seqnum = grb.stepRange
                elif grb.productDefinitionTemplateNumber == 8:
                    seqnum = grb.endStep
                else:
                    raise Exception('error seq field')
                '''
                if seqfield == GribTypes.endStep:
                    seqnum = grb.endStep
                elif seqfield == GribTypes.stepRange:
                    seqnum = grb.stepRange
                else:
                    raise Exception('error seq field')
                '''

                if seq_key_is_num:
                    seqnum = int(seqnum)

                pnum = 0
                if pnumfield == None:
                    pass
                elif pnumfield == GribTypes.perturbationNumber:
                    pnum = grb.perturbationNumber
                else:
                    raise Exception('error pnum field')

                curkey = None
                if seq_key_is_num:
                    curkey = seqnum
                else:
                    curkey = str(seqnum) if pnum == 0 else str(pnum) + '_' + str(seqnum)

                if seq_and_p_num is None:
                    rst[curkey] = grb
                else:
                    if curkey in seq_and_p_num:
                        rst[curkey] = grb

            logger.info('FixReadData read_gribdata_from_grib2_with_pygrib_single_file_seqnum over %s' % (str(params)))
            return rst
        except Exception as data:
            logger.error('FixReadData read_gribdata_from_grib2_with_pygrib_single_file_seqnum except %s %s' % (str(params), str(data)))

            return None
        
if __name__ == '__main__':
    print('done')
