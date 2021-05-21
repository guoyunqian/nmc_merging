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

        seqfield = params[FixParamTypes.SeqField] if FixParamTypes.SeqField in params else GribTypes.endStep
        pnumfield = params[FixParamTypes.PNumField] if FixParamTypes.PNumField in params else None   #GribTypes.perturbationNumber
        
        try:
            import pygrib
            #LogLib.logger.info('FixReadData read_gribdata_from_grib2_with_pygrib_single_file_seqnum start %s' % (str(params)))
            
            rst = {}
            grbs = pygrib.open(from_file)
            for grb in grbs:
                seqnum = 0
                if seqfield == GribTypes.endStep:
                    seqnum = grb.endStep
                elif seqfield == GribTypes.stepRange:
                    seqnum = grb.stepRange
                else:
                    raise Exception('error seq field')

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

            #LogLib.logger.info('FixReadData read_gribdata_from_grib2_with_pygrib_single_file_seqnum over %s' % (str(params)))
            return rst
        except Exception as data:
            #LogLib.logger.error('FixReadData read_gribdata_from_grib2_with_pygrib_single_file_seqnum except %s %s' % (str(params), str(data)))

            return None
        
if __name__ == '__main__':
    print('done')
