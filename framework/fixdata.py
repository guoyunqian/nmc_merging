#!/usr/bin/python
# -*- coding: utf-8 -*-
#Filename: fixdata.py

'''
Created on Aug 21, 2020

@author: anduin
'''

import os
import datetime

from publictype.fixproctypes import FixProcTypes
from publictype.fixparamtypes import FixParamTypes

class FixData(object):
    def __init__(self, logger=None):
        self.logger = logger

	#一次确定出所有时间点需要的源文件和目标文件全路径
    #当前用于app数据源融合
    def fix_data_muldst_notime(self, params, quit_when_error=False):
        try:
            self.logger.info('FixData fix_data_muldst_notime start')

            dt_list = []
            if FixProcTypes.DTList in params:
                dt_list = params[FixProcTypes.DTList][0](params[FixProcTypes.DTList][1])

            self.logger.debug('FixData fix_data_muldst_notime dt_list:%s' % str(dt_list))

            flistparams = params[FixProcTypes.FileList][1]
            flistparams[FixParamTypes.DTS] = dt_list

            savefullpaths, fixfullpath, sdt = params[FixProcTypes.FileList][0](flistparams)
            if fixfullpath == None:
                self.logger.warning('FixData fix_data_muldst_notime process datetime no file %s' % (str(flistparams)))
                return
            
            if savefullpaths is None or len(savefullpaths) == 0:
                self.logger.warning('FixData fix_data_muldst_notime process datetime not need process %s' % (str(flistparams)))
                return

            self.logger.debug('FixData fix_data_muldst_notime process fixfullpath %s' % (fixfullpath))

            readparams = params[FixProcTypes.ReadData][1]
            readparams[FixParamTypes.SFullPath] = fixfullpath
            readparams[FixParamTypes.SeqAndPNum] = list(savefullpaths.keys())

            grdlist = params[FixProcTypes.ReadData][0](readparams)
            if grdlist is None:
                self.logger.error('FixData fix_data_muldst_notime read file error %s %s' % (fixfullpath, str(savefullpaths)))
                return

            wparams = params[FixProcTypes.WriteData][1]
            wparams[FixParamTypes.GridDataList] = grdlist
            wparams[FixParamTypes.DFullPaths] = savefullpaths
            wparams[FixParamTypes.DT] = sdt

            if params[FixProcTypes.WriteData][0](wparams):
                self.logger.info('FixData fix_data_muldst_notime process file over %s %s' % (fixfullpath, str(savefullpaths)))
            else:
                self.logger.error('FixData fix_data_muldst_notime write file error %s %s' % (fixfullpath, str(savefullpaths)))

            self.logger.info('FixData fix_data_muldst_notime over')
        except Exception as data:
            self.logger.error('FixData fix_data_muldst_notime except %s' % (str(data)))
            
if __name__ == '__main__':
    print('done')
