#!/usr/bin/python
# -*- coding: utf-8 -*-
#Filename: cfg_srcdata.py

'''
Created on Apr 26, 2021

@author: anduin
'''

import os
import datetime

import public
from publictype.fixparamtypes import FixParamTypes as FixParamTypes
import backupfunc.backupfuncs as backup_funcs
import backupfunc.func_forword as backup_func_forword
import backupfunc.func_datasource as backup_func_datasource
import backupfunc.func_missing as backup_func_missing

import checkfunc.checkfuncs as check_funcs

class CfgSrcData(object):
    def __init__(self, logger):
        self.logger = logger

        #配置文件路径
        self.path = None
        #数据源的信息
        self.srcinfos = None
        
        self.backupcfglist = None

        self.checkcfglist = None

        self.srclist = None

    def parse_src_config(self, cfg):
        self.srcinfos = {}

        section = 'config'
        #path
        rst = public.get_opt_str(cfg, section, 'path')
        if rst is None:
            raise Exception('config path error')

        self.srcinfos[FixParamTypes.SDict] = rst

        #fn_fmt
        rst = public.get_opt_str(cfg, section, 'fn_fmt')
        if rst is None:
            raise Exception('config fn_fmt error')

        self.srcinfos[FixParamTypes.SFnFmt] = rst
        
        #fhs
        rst = public.get_opt_str(cfg, section, 'fhs')
        if rst is None:
            raise Exception('config fhs error')
        
        fhs = public.parse_list(rst, is_num=True, right_c=True)
        if len(fhs) == 0:
            fhs = None

        self.srcinfos[FixParamTypes.SFHS] = fhs
        
        #seq
        rst = public.get_opt_str(cfg, section, 'seq')
        if rst is None:
            raise Exception('config seq error')
        
        seq = public.parse_list(rst, is_num=True, right_c=True)
        if len(seq) == 0:
            seq = None

        self.srcinfos[FixParamTypes.SSeq] = seq
        
        #数据生成时间，大于起报时的时间，如果不设值，代表不检查
        rst = public.get_opt_str(cfg, section, 'f_delta')
        if rst is None:
            raise Exception('config f_delta error')
        
        if len(rst) == 0:
            rst = None
        else:
            rst = public.parse_list(rst, is_num=True, right_c=True)

        self.srcinfos[FixParamTypes.SFDelta] = rst
        
        #提前多久生成起报时的数据
        rst = public.get_opt_int(cfg, section, 'fhs_delta')
        if rst is None:
            raise Exception('config fhs_delta error')
        
        self.srcinfos[FixParamTypes.SFhsDelta] = rst

        #完整的数据优先
        rst = public.get_opt_str(cfg, section, 'complete_data_preferred')
        if rst is None:
            raise Exception('config complete_data_preferred error')
        
        if rst.lower() == 'false':
            rst = False
        elif rst.lower() == 'true':
            rst = True
        else:
            raise Exception('config complete_data_preferred error value %s' % rst)

        self.srcinfos[FixParamTypes.ComPreferred] = rst

        #经度格点数
        rst = public.get_opt_int(cfg, section, 'nlon')
        if rst is None:
            raise Exception('config nlon error')
        
        self.srcinfos[FixParamTypes.NLon] = rst

        #纬度格点数
        rst = public.get_opt_int(cfg, section, 'nlat')
        if rst is None:
            raise Exception('config nlat error')
        
        self.srcinfos[FixParamTypes.NLat] = rst

        #开始经度
        rst = public.get_opt_float(cfg, section, 'slon')
        if rst is None:
            raise Exception('config slon error')
        
        self.srcinfos[FixParamTypes.SLon] = rst

        #开始纬度
        rst = public.get_opt_float(cfg, section, 'slat')
        if rst is None:
            raise Exception('config slat error')
        
        self.srcinfos[FixParamTypes.SLat] = rst

        #结束经度
        rst = public.get_opt_float(cfg, section, 'elon')
        if rst is None:
            raise Exception('config elon error')
        
        self.srcinfos[FixParamTypes.ELon] = rst

        #结束纬度
        rst = public.get_opt_float(cfg, section, 'elat')
        if rst is None:
            raise Exception('config elat error')
        
        self.srcinfos[FixParamTypes.ELat] = rst

        #经度分辨率
        rst = public.get_opt_float(cfg, section, 'dlon')
        if rst is None:
            raise Exception('config dlon error')
        
        self.srcinfos[FixParamTypes.DLon] = rst

        #纬度分辨率
        rst = public.get_opt_float(cfg, section, 'dlat')
        if rst is None:
            raise Exception('config dlat error')
        
        self.srcinfos[FixParamTypes.DLat] = rst

    #解析数据备份方法的配置信息
    def parse_backup_config(self, cfg, logger=None):
        self.backupcfglist = []

        section_fmt = 'backup%02d'

        index = 1
        while(True):
            section = section_fmt % index
            index += 1

            if not cfg.has_section(section):
                break

            backupcfg = {}

            #备份方法
            rst = public.get_opt_str(cfg, section, 'func')
            if rst is None:
                raise Exception('%s func error' % section)
            
            backupcfg[FixParamTypes.FuncName] = rst

            backup_funcs.get_func_params(rst, cfg, section, backupcfg, logger if logger else self.logger)

            self.backupcfglist.append(backupcfg)

    #解析数据检查方法的配置信息
    def parse_check_config(self, cfg, logger=None):
        self.checkcfglist = []

        section_fmt = 'check%02d'

        index = 1
        while(True):
            section = section_fmt % index
            index += 1

            if not cfg.has_section(section):
                break

            checkcfg = {}

            #备份方法
            rst = public.get_opt_str(cfg, section, 'func')
            if rst is None:
                raise Exception('%s func error' % section)
            
            checkcfg[FixParamTypes.FuncName] = rst

            check_funcs.get_func_params(rst, cfg, section, checkcfg, logger if logger else self.logger)

            self.checkcfglist.append(checkcfg)
            
    #组成数据源的信息列表，依次从数据源中获取数据即可
    def proc_all_src(self):
        self.srclist = []

        self.srclist.append([self, 0])

        for backupcfg in self.backupcfglist:
            if backupcfg[FixParamTypes.FuncName] == backup_func_forword.func_name:
                for delta in backupcfg[FixParamTypes.Deltas]:
                    self.srclist.append([self, delta])
            elif backupcfg[FixParamTypes.FuncName] == backup_func_datasource.func_name:
                dscfg = CfgSrcData()
                dscfgpath = backupcfg[FixParamTypes.CfgFilePath]
                if not os.path.isabs(dscfgpath):
                    dscfgpath = os.path.join(os.path.dirname(self.inipath), dscfgpath)

                dscfg.parse(inipath=dscfgpath, need_backup=False)

                for delta in backupcfg[FixParamTypes.Deltas]:
                    self.srclist.append([dscfg, delta])
            elif backupcfg[FixParamTypes.FuncName] == backup_func_missing.func_name:
                pass
            else:
                raise Exception('unknown function name %s' % backupcfg[FixParamTypes.FuncName])
            

    def parse(self, inipath=None, need_backup=True, logger=None):
        try:
            if inipath is None:
                inipath = self.path
            else:
                self.path = inipath

            if inipath is None:
                print('CfgSrcData ini path is none')
                self.logger.error('CfgSrcData ini path is none')
                return None

            cfgobj = public.parse_ini_file(inipath)
            if cfgobj is None:
                print('CfgSrcData ini params error')
                self.logger.error('CfgSrcData ini params error')
                return None

            self.parse_src_config(cfgobj)

            if need_backup:
                self.parse_backup_config(cfgobj)

                self.proc_all_src()

            self.parse_check_config(cfgobj)

            return True
        except Exception as data:
            self.logger.error('CfgSrcData parse except %s' % (str(data)))
            return False
            
    '''
    def setparams(self, params, index=-1):
        params.update(self.cfginfos)
        '''

if __name__ == '__main__':
    print('done')
