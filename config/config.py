#!/usr/bin/python
# -*- coding: utf-8 -*-
#Filename: config.py

'''
Created on Apr 26, 2021

@author: anduin
'''

import os
import datetime

from logmodule.loglib import *
import public
from publictype.fixparamtypes import FixParamTypes as FixParamTypes
from config.subconfig import SubConfig

class Config(object):
    def __init__(self):
        self.path = None
        self.cfginfos = None

        self.subcfgobjlist = None

    def parse(self, inipath=None):
        try:
            LogLib.logger.info('config ini parse start')

            if inipath is None:
                inipath = self.path
            else:
                self.path = inipath

            if inipath is None:
                print('config ini path is none')
                LogLib.logger.error('config ini path error')
                return None

            cfgobj = public.parse_ini_file(inipath)
            if cfgobj is None:
                print('config ini params error')
                LogLib.logger.error('config ini params error')
                return None

            subcfginfos = public.parse_ini_mulinfos(cfgobj, 'Config', 'config%02d')
            if subcfginfos is None or len(subcfginfos) == 0:
                print('no sub config ini')
                LogLib.logger.error('config ini no sub config ini')
                return None

            self.cfginfos = {}
            #self.cfginfos[FixParamTypes.CfgObjList] = []
            self.subcfgobjlist = []

            cfgbasedir = os.path.dirname(inipath)
            for subcfginfo in subcfginfos:
                subcfgpath = os.path.join(cfgbasedir, subcfginfo)
                subcfgobj = SubConfig()
                subinfos = subcfgobj.parse(subcfgpath)
                if subinfos is None:
                    LogLib.logger.error('config ini parse sub config error')
                    return None

                self.subcfgobjlist.append(subcfgobj)

            LogLib.logger.info('config ini parse over')

            return self.cfginfos
        except Exception as data:
            LogLib.logger.error('config ini parse except %s' % (str(data)))
            return None
            
    def setparams(self, params, index=0):
        self.subcfgobjlist[index].setparams(params)

        params.update(self.cfginfos)

if __name__ == '__main__':
    cfg = Config()
    print
    print('done')
