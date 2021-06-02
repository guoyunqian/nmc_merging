#!/usr/bin/python
# -*- coding: utf-8 -*-
#Filename: cfg_main.py

'''
Created on Apr 26, 2021

@author: anduin
'''

import os
import datetime

import public
from publictype.fixparamtypes import FixParamTypes as FixParamTypes
from cfg_srcdata import CfgSrcData
import procfunc.procfuncs as proc_funcs

class CfgMain(object):
    def __init__(self, logger):
        self.logger = logger

        #配置文件路径
        self.path = None
        #保存数据的信息
        self.savecfginfos = None
        #保存grib2的信息
        self.grib2cfginfos = None
        #数据源列表
        self.srccfglist = None
        #处理过程列表
        self.proccfglist = None

    #保存结果的信息
    def parse_save_config(self, cfg):
        self.savecfginfos = {}

        section = 'save_config'

        #path
        rst = public.get_opt_str(cfg, section, 'path')
        if rst is None:
            raise Exception('save_config path error')

        self.savecfginfos[FixParamTypes.DDict] = rst

        #fn_fmt
        rst = public.get_opt_str(cfg, section, 'fn_fmt')
        if rst is None:
            raise Exception('save_config fn_fmt error')

        self.savecfginfos[FixParamTypes.DFnFmt] = rst
        
        #fhs
        rst = public.get_opt_str(cfg, section, 'fhs')
        if rst is None:
            raise Exception('save_config fhs error')
        
        fhs = public.parse_list(rst, is_num=True, right_c=True)
        if len(fhs) == 0:
            fhs = None

        self.savecfginfos[FixParamTypes.DFHS] = fhs
        
        #seq
        rst = public.get_opt_str(cfg, section, 'seq')
        if rst is None:
            raise Exception('save_config seq error')
        
        seq = public.parse_list(rst, is_num=True, right_c=True)
        if len(seq) == 0:
            seq = None

        self.savecfginfos[FixParamTypes.DSeq] = seq
        
        #提前多久生成起报时的数据
        rst = public.get_opt_int(cfg, section, 'fhs_delta')
        if rst is None:
            raise Exception('save_config fhs_delta error')
        
        self.savecfginfos[FixParamTypes.DFhsDelta] = rst

        #数据精度
        rst = public.get_opt_int(cfg, section, 'decimals')
        if rst is None:
            raise Exception('save_config decimals error')
        
        self.savecfginfos[FixParamTypes.Decimals] = rst

        #经纬度精度
        rst = public.get_opt_int(cfg, section, 'scale_decimals')
        if rst is None:
            raise Exception('save_config scale_decimals error')
        
        self.savecfginfos[FixParamTypes.ScaleDecimals] = rst

        #经度格点数
        rst = public.get_opt_int(cfg, section, 'nlon')
        if rst is None:
            raise Exception('save_config nlon error')
        
        self.savecfginfos[FixParamTypes.NLon] = rst

        #纬度格点数
        rst = public.get_opt_int(cfg, section, 'nlat')
        if rst is None:
            raise Exception('save_config nlat error')
        
        self.savecfginfos[FixParamTypes.NLat] = rst

        #开始经度
        rst = public.get_opt_float(cfg, section, 'slon')
        if rst is None:
            raise Exception('save_config slon error')
        
        self.savecfginfos[FixParamTypes.SLon] = rst

        #开始纬度
        rst = public.get_opt_float(cfg, section, 'slat')
        if rst is None:
            raise Exception('save_config slat error')
        
        self.savecfginfos[FixParamTypes.SLat] = rst

        #结束经度
        rst = public.get_opt_float(cfg, section, 'elon')
        if rst is None:
            raise Exception('save_config elon error')
        
        self.savecfginfos[FixParamTypes.ELon] = rst

        #结束纬度
        rst = public.get_opt_float(cfg, section, 'elat')
        if rst is None:
            raise Exception('save_config elat error')
        
        self.savecfginfos[FixParamTypes.ELat] = rst

        #经度分辨率
        rst = public.get_opt_float(cfg, section, 'dlon')
        if rst is None:
            raise Exception('save_config dlon error')
        
        self.savecfginfos[FixParamTypes.DLon] = rst

        #纬度分辨率
        rst = public.get_opt_float(cfg, section, 'dlat')
        if rst is None:
            raise Exception('save_config dlat error')
        
        self.savecfginfos[FixParamTypes.DLat] = rst
        
        #是否保存m4格式
        rst = public.get_opt_int(cfg, section, 'save_m4')
        if rst is None:
            raise Exception('save_config save_m4 error')
        
        self.savecfginfos[FixParamTypes.SaveM4] = rst
        
        #m4文件保存路径
        rst = public.get_opt_str(cfg, section, 'path_m4')
        if rst is None:
            raise Exception('save_config path_m4 error')

        self.savecfginfos[FixParamTypes.DDictM4] = rst
        
    #保存grib2的信息
    def parse_grib2_config(self, cfg):
        self.grib2cfginfos = {}

        section = 'grib_config'

        #exec_fmt
        rst = public.get_opt_str(cfg, section, 'exec_fmt')
        #if rst is None:
        #    raise Exception('grib_config exec_fmt error')

        self.grib2cfginfos[FixParamTypes.ExecFmt] = rst

    #解析源数据的信息
    def parse_data_config(self, cfg, basedir, logger=None):
        if logger is None:
            logger = self.logger
            
        self.srccfglist = []

        section_fmt = 'data%02d'

        index = 1
        while(True):
            section = section_fmt % index
            index += 1

            if not cfg.has_section(section):
                break

            srccfg = {}

            srccfg[FixParamTypes.DatasName] = section

            #数据源配置文件
            rst = public.get_opt_str(cfg, section, 'data')
            if rst is None:
                raise Exception('%s data error' % section)

            if os.path.isabs(rst):
                srccfg[FixParamTypes.CfgFilePath] = rst
            else:
                srccfg[FixParamTypes.CfgFilePath] = os.path.join(basedir, rst)

            cfgobj = CfgSrcData(logger)
            cfgobj.parse(srccfg[FixParamTypes.CfgFilePath])
            srccfg[FixParamTypes.CfgObj] = cfgobj

            #对应结果的时效
            rst = public.get_opt_str(cfg, section, 'seq')
            if rst is None:
                raise Exception('%s seq error' % section)
        
            seq = public.parse_list(rst, is_num=True, right_c=True)
            if len(seq) == 0:
                seq = None

            srccfg[FixParamTypes.DSeq] = seq
            
            #日志文件
            rst = public.get_opt_str(cfg, section, 'logfile')
            if rst is None:
                raise Exception('%s logfile error' % section)

            srccfg[FixParamTypes.LogFilePath] = rst

            self.srccfglist.append(srccfg)
            
    #解析数据处理方法的配置信息
    def parse_proc_config(self, cfg, logger=None):
        self.proccfglist = []

        section_fmt = 'proc%02d'

        index = 1
        while(True):
            section = section_fmt % index
            index += 1

            if not cfg.has_section(section):
                break

            proccfg = {}

            #处理方法
            rst = public.get_opt_str(cfg, section, 'func')
            if rst is None:
                raise Exception('%s func error' % section)
            
            proccfg[FixParamTypes.FuncName] = rst

            proc_funcs.get_func_params(rst, cfg, section, proccfg, logger if logger else self.logger)

            self.proccfglist.append(proccfg)

    #解析主配置文件
    def parse(self, inipath=None, logger=None):
        try:
            if logger is None:
                logger = self.logger

            logger.info('config ini parse start')

            if inipath is None:
                inipath = self.path
            else:
                self.path = inipath

            if inipath is None:
                print('config ini path is none')
                logger.error('config ini path error')
                return False

            cfgobj = public.parse_ini_file(inipath, logger)
            if cfgobj is None:
                print('config ini params error')
                logger.error('config ini params error')
                return False

            self.parse_save_config(cfgobj)

            self.parse_grib2_config(cfgobj)

            cfgbasedir = os.path.dirname(inipath)
            self.parse_data_config(cfgobj, cfgbasedir, logger)

            self.parse_proc_config(cfgobj, logger)

            logger.info('config ini parse over')

            return True
        except Exception as data:
            logger.error('config ini parse except %s' % (str(data)))
            return False
            
    '''
    #设置读取该数据源或者该数据源备份的参数
    def setparams(self, params, index, backupindex):
        if backupindex is None:
            #self.srccfglist[index].setparams(params)

            params.update(self.cfginfos)
        else:
            pass
        '''
    '''
    #判断从数据源获得的数据是否完整
    def need_backup(self, rsts, index):
        need_seq_set = set(self.srccfglist[index][FixParamTypes.SSeq])
        datas_name = self.srccfglist[index][FixParamTypes.DatasName]
        exist_seq_set = set(list(rsts[datas_name].keys()))
        
        return (len(need_seq_set.difference(exist_seq_set)) > 0)
    '''

if __name__ == '__main__':
    cfg = CfgMain()
    
    print('done')
