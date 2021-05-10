#!/usr/bin/python
# -*- coding: utf-8 -*-
#Filename: fixrecorddata.py

"""
Created on Mar 23, 2021

@author: anduin
"""

import os
import json

from logmodule.loglib import *
from publictype.fixparamtypes import FixParamTypes

class FixRecordData(object):
    #每个文件有两个时间，一个是上次读取文件的时效，一个是上次读取文件的修改时间。
    def read_dtinfos(self, params):
        rec_path = None

        if type(params) is dict:
            rec_path = params[FixParamTypes.RecordPath]
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
            LogLib.logger.error('FixMulData read_dtinfos except %s %s' % (str(params), str(data)))

            return None

    def save_dtinfos(self, params):
        rec_data = params[FixParamTypes.RecordData]
        rec_path = params[FixParamTypes.RecordPath]

        try:
            with open(rec_path, 'w') as f:
                json.dump(rec_data, f)

            return True
        except Exception as data:
            LogLib.logger.error('FixMulData save_dtinfos except %s %s' % (str(params), str(data)))

            return False


if __name__ == '__main__':
    print('done')
