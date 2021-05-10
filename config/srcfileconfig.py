#!/usr/bin/python
# -*- coding: utf-8 -*-
#Filename: srcfileconfig.py

'''
Created on Apr 26, 2021

@author: anduin
'''

import os
import datetime

from logmodule.loglib import *
import public
from publictype.fixparamtypes import FixParamTypes as FixParamTypes

class SrcFileConfig(object):
    def __init__(self):
        self.path = None
        self.cfginfos = None

    def parse(self, inipath=None):
        try:
            if inipath is None:
                inipath = self.path
            else:
                self.path = inipath

            if inipath is None:
                print('SrcFileConfig ini path is none')
                LogLib.logger.error('SrcFileConfig ini path is none')
                return None

            cfgobj = public.parse_ini_file(inipath)
            if cfgobj is None:
                print('SrcFileConfig ini params error')
                LogLib.logger.error('SrcFileConfig ini params error')
                return None

            self.cfginfos = {}

            #
            rst = public.get_opt_str(cfgobj, 'Config', 'fix_path')
            if rst is None or len(rst) == 0:
                LogLib.logger.error('SrcFileConfig Config fix_path error')
                return None

            self.cfginfos[FixParamTypes.SDict] = rst

            #
            rst = public.get_opt_str(cfgobj, 'Config', 'fix_fn_fmt')
            if rst is None or len(rst) == 0:
                LogLib.logger.error('SrcFileConfig Config fix_fn_fmt error')
                return None

            self.cfginfos[FixParamTypes.SFnFmt] = rst
            
            #
            rst = public.get_opt_str(cfgobj, 'Config', 'fix_fhs')
            if rst is None or len(rst) == 0:
                LogLib.logger.error('SrcFileConfig Config fix_fhs error')
                return None

            sfhs = public.parse_list(rst)
            self.cfginfos[FixParamTypes.SFHS] = sfhs
            
            #
            rst = public.get_opt_str(cfgobj, 'Config', 'fix_seq')
            if rst is None or len(rst) == 0:
                LogLib.logger.error('SrcFileConfig Config fix_seq error')
                return None

            sseq = public.parse_list(rst)
            self.cfginfos[FixParamTypes.SSeq] = sseq
            
            #
            rst = public.get_opt_int(cfgobj, 'Config', 'fix_f_delta')
            #if rst is None:
            #    LogLib.logger.error('SrcFileConfig Config fix_f_delta error')
            #    return None

            self.cfginfos[FixParamTypes.SFDelta] = rst
            
            #
            rst = public.get_opt_int(cfgobj, 'Config', 'fix_fhs_delta')
            #if rst is None:
            #    LogLib.logger.error('SrcFileConfig Config fix_fhs_delta error')
            #    return None

            self.cfginfos[FixParamTypes.SFhsDelta] = rst
            
            return self.cfginfos
        except Exception as data:
            LogLib.logger.error('SrcFileConfig parse except %s' %s (str(data)))
            return None
            
    def setparams(self, params):
        params.update(self.cfginfos)

if __name__ == '__main__':
    print('done')
