#!/usr/bin/python
# -*- coding: utf-8 -*-
#Filename: fixrecorddata.py

"""
Created on Mar 23, 2021

@author: anduin
"""

import os
import json

from publictype.fixparamtypes import FixParamTypes

class FixRecordData(object):
    def __init__(self, logger):
        self.logger = logger
        
    #每个文件有两个时间，一个是上次读取文件的时效，一个是上次读取文件的修改时间。
    def read_dtinfos(self, params):
        rec_path = None
        logger = self.logger

        if type(params) is dict:
            rec_path = params[FixParamTypes.RecordPath]
            if FixParamTypes.CurLogger in params and params[FixParamTypes.CurLogger] is not None:
                logger = params[FixParamTypes.CurLogger]

        elif type(params) is str:
            rec_path = params
        else:
            return None

        try:
            if os.path.exists(rec_path):
                with open(rec_path, 'r') as f:
                    return json.load(f)
            else:
                return {}
        except Exception as data:
            self.logger.error('FixMulData read_dtinfos except %s %s' % (str(params), str(data)))

            return None

    def save_dtinfos(self, params):
        rec_data = params[FixParamTypes.RecordData]
        rec_path = params[FixParamTypes.RecordPath]
        
        logger = params[FixParamTypes.CurLogger] if FixParamTypes.CurLogger in params else None
        if logger is None:
            logger = self.logger

        try:
            with open(rec_path, 'w') as f:
                json.dump(rec_data, f)

            return True
        except Exception as data:
            logger.error('FixMulData save_dtinfos except %s %s' % (str(params), str(data)))

            return False


if __name__ == '__main__':
    print('done')
