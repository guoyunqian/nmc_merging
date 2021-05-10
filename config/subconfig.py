#!/usr/bin/python
# -*- coding: utf-8 -*-
#Filename: subconfig.py

'''
Created on Apr 26, 2021

@author: anduin
'''

import os
import datetime

from logmodule.loglib import *
import public
from publictype.fixparamtypes import FixParamTypes as FixParamTypes
from config.srcfileconfig import SrcFileConfig

class SubConfig(object):
    def __init__(self):
        self.path = None
        self.cfginfos = None

        self.srccfgobj = None

    def parse(self, inipath=None):
        try:
            if inipath is None:
                inipath = self.path
            else:
                self.path = inipath

            if inipath is None:
                print('SubConfig ini path is none')
                LogLib.logger.error('SubConfig ini path is none')
                return None

            cfgobj = public.parse_ini_file(inipath)
            if cfgobj is None:
                print('SubConfig ini params error')
                LogLib.logger.error('SubConfig ini params error')
                return None

            srccfginfo = public.get_opt_str(cfgobj, 'Src_Config', 'src_file_infos')
            if srccfginfo is None or len(srccfginfo) == 0:
                print('SubConfig no src file config ini')
                LogLib.logger.error('SubConfig no src file config ini')
                return None

            srcbasedir = os.path.dirname(inipath)
            srccfgpath = os.path.join(srcbasedir, srccfginfo)
            srccfgobj = SrcFileConfig()
            srcinfos = srccfgobj.parse(srccfgpath)
            if srcinfos is None:
                LogLib.logger.error('SubConfig src file parse error')
                return None

            self.srccfgobj = srccfgobj

            self.cfginfos = {}

            #
            rst = public.get_opt_str(cfgobj, 'Save_Config', 'save_path')
            if rst is None or len(rst) == 0:
                LogLib.logger.error('SubConfig Save_Config save_path error')
                return None

            self.cfginfos[FixParamTypes.DDict] = rst

            #
            rst = public.get_opt_str(cfgobj, 'Save_Config', 'save_fn_fmt')
            if rst is None or len(rst) == 0:
                LogLib.logger.error('SubConfig Save_Config save_fn_fmt error')
                return None

            self.cfginfos[FixParamTypes.DFnFmt] = rst
            
            #
            rst = public.get_opt_str(cfgobj, 'Save_Config', 'save_fhs')
            if rst is None or len(rst) == 0:
                LogLib.logger.error('SubConfig Save_Config save_fhs error')
                return None

            dfhs = public.parse_list(rst)
            self.cfginfos[FixParamTypes.DFHS] = dfhs
            
            #
            rst = public.get_opt_str(cfgobj, 'Save_Config', 'save_seq')
            if rst is None or len(rst) == 0:
                LogLib.logger.error('SubConfig Save_Config save_seq error')
                return None

            dseq = public.parse_list(rst)
            self.cfginfos[FixParamTypes.DSeq] = dseq
            
            #
            rst = public.get_opt_str(cfgobj, 'Save_Config', 'save_seq_fmt')
            if rst is None or len(rst) == 0:
                LogLib.logger.error('SubConfig Save_Config save_seq_fmt error')
                return None

            dseqfmt = eval(rst)
            self.cfginfos[FixParamTypes.DSeqFmt] = dseqfmt
            
            #
            rst = public.get_opt_int(cfgobj, 'Save_Config', 'save_fhs_delta')
            #if rst is None:
            #    LogLib.logger.error('SubConfig Save_Config save_fhs_delta error')
            #    return None

            self.cfginfos[FixParamTypes.DFhsDelta] = rst
            
            #
            rst = public.get_opt_str(cfgobj, 'RecordFile', 'record_path')
            if rst is None or len(rst) == 0:
                LogLib.logger.error('SubConfig RecordFile record_path error')
                return None

            self.cfginfos[FixParamTypes.RecordPath] = rst
            
            return self.cfginfos
        except Exception as data:
            LogLib.logger.error('SubConfig except %s' % (str(data)))
            return None
            
    def setparams(self, params):
        self.srccfgobj.setparams(params)

        params.update(self.cfginfos)

if __name__ == '__main__':
    print('done')
