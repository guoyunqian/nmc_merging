#!/usr/bin/python
# -*- coding: utf-8 -*-
#Filename: nmc_merging.py

"""
Created on Nov 23, 2020

@author: anduin
"""

import os
import sys
import datetime

from logmodule.loglib import *
from publictype.fixproctypes import FixProcTypes
from publictype.fixparamtypes import FixParamTypes
from publictype.fixfileTypes import FixFileTypes
from publictype.gribtypes import GribTypes
import public
#import config
from config.config import Config
from config.subconfig import SubConfig
from config.srcfileconfig import SrcFileConfig

from framework.fixfileinfos import FixFileInfos
from framework.fixreaddata import FixReadData
from framework.fixwritedata import FixWriteData
from framework.fixrecorddata import FixRecordData
from framework.fixdata import FixData

#时间设定应该是和s_is_bjt保持一致，s_is_bjt是true，这两个时间就应该是北京时间，否则是utc时间
#结束时间和小时数（t_num）不会同时使用到，分别对应不同的获取时间列表的函数
#用于回算
#fix_stime = datetime.datetime(2021,3,29,8,0,0)
#fix_etime = datetime.datetime(2021,4,1,8,0,0)
#用于实时，类似于使用t_num
'''
def get_etime():
    curutcdt = datetime.datetime.utcnow().replace(second=0,microsecond=0)
    if curutcdt.minute >= 10 and curutcdt.minute < 30:
        return curutcdt.replace(minute=0) - datetime.timedelta(hours=1)
    else:
        return curutcdt.replace(minute=0)
    '''
#fix_etime = get_etime()
fix_etime = datetime.datetime.now().replace(minute=0,second=0,microsecond=0)
#fix_stime = fix_etime - datetime.timedelta(hours=12)

#文件的时间
#fdt = None

#回推小时数
#t_num = 24*2

#源文件名中的时间是否是北京时间
s_is_bjt = True
#目标文件名中的时间是否是北京时间
d_is_bjt = True

#获取时间列表时，每个时间的最小间隔
delta_t = 60

#预报是08时，实况为8点到13点
#deltas = list(range(0, 6*60, 60))

#确定文件的时间差
s_f_delta = None
s_f_deltas = None

s_fhs_delta = None
s_fhs_deltas = None

d_fhs_delta = int(2.5*60)

#源文件目录
fix_dict = None
fix_dicts = None

#目标文件目录
save_dict = None

#dt_fmt = [[['ITFMT', '%Y%m%d%H']], [['ITFMT', '%Y%m%d%H']]]

#源文件名
fix_fn_fmt = None
fix_fn_fmts = None

#目标文件名
save_fn_fmt = None

#获取时间时，需要选择的小时，使用range获得，或者直接用list指定
s_fhs = None
s_fhs_s = None

save_fhs = None

#预报时效
s_seq = None
d_seq = None
s_seq_s = None
d_seq_s = None

#时效格式
d_seq_fmt = None

#decimals = 3
#ns_to_s = 10**-9

#记录文件路径
dtinfospath = None
#上次处理的文件的修改时间
#{'QPE':dt,'SCMOC':dt,'SMERGE':dt}
dtinfos = None

#f_type = None
#fm_type = None

#columns=[ColumnNames.StaID.value, ColumnNames.TMX.value]

#workdir = os.path.dirname(__file__)
#stafilepath = os.path.join(workdir, 'station_2401.dat')

#stabaseinfos = public.get_stations_from_csv(stafilepath, dropcol=[1,2,3], columns=[ColumnNames.StaID.value, ColumnNames.Area.value])
#stabaseinfos[ColumnNames.Result.value] = 0
#filters = [ [ColumnNames.Seq.value, ConditionTypes.Equal, 24] ]

#sumgrd = copy.deepcopy(stabaseinfos)
#sumgrd[ColumnNames.Result.value] = 0

#日志文件存储目录
log_file_dir = 'logfiles'
#日志文件的文件名
log_file_name = 'nmc_merging.log'

#配置文件存储目录
cfg_file_dir = 'config'
#日志文件的文件名
cfg_file_name = 'config.ini'

#def get_seqnum_from_fn(fname):
#    return int(int(fname[-11:-8]) / 60)

def init_log(logfile):
    LogLib.init()
    LogLib.addTimedRotatingFileHandler(logfile)
    LogLib.setLevel(logging.DEBUG)
    
def uninit_log():
    LogLib.uninit()
    
def proc():
    #fftime = FixFileTime()
    ffinfos = FixFileInfos()
    frdata = FixReadData()
    #fmdata = FixModifyData()
    #fmuldata = FixMulData()
    fwdata = FixWriteData()
    frecdata = FixRecordData()
    fdata = FixData()
    
    global dtinfos
    dtinfos = frecdata.read_dtinfos(dtinfospath)
    if dtinfos is None:
        LogLib.logger.error('记录文件读取失败。')

        return

    '''
    dtlistparams = { FixParamTypes.STime:fix_stime, FixParamTypes.ETime:fix_etime, FixParamTypes.RangeDelta:delta_t,
                    FixParamTypes.RangeDelta_OBS:delta_t_obs, FixParamTypes.Deltas:deltas
                    }
                    '''
    '''
    fixdelta = 0
    if s_is_bjt != d_is_bjt:
        if s_is_bjt:
            fixdelta = -8
        else:
            fixdelta = 8
            '''
    #f_delta = 18
    #if not s_is_bjt:
    #    f_delta += 8*60
        
    filelistparams = { FixParamTypes.SDict:fix_dict, FixParamTypes.SFnFmt:fix_fn_fmt, FixParamTypes.DDict:save_dict,
                      FixParamTypes.DFnFmt:save_fn_fmt, FixParamTypes.DT:fix_etime, FixParamTypes.SSeq:s_seq,
                      FixParamTypes.DSeq:d_seq, FixParamTypes.DSeqFmt:d_seq_fmt, FixParamTypes.SFHS:s_fhs,
                      FixParamTypes.DFHS:save_fhs, FixParamTypes.SFDelta:s_f_delta, FixParamTypes.DFhsDelta:d_fhs_delta
                      }

    readdataparams = { FixParamTypes.SeqField:GribTypes.stepRange
                      }
    '''
    muldataparams = { FixParamTypes.DstGridData:sumgrd, FixParamTypes.SName:ColumnNames.TMX.value,
                     FixParamTypes.DName:ColumnNames.Result.value, FixParamTypes.Columns:columns
                     }
                     '''

    writedataparams = { 
                       }
    
    #recorddataparams = { FixParamTypes.RecordData:dtinfos, FixParamTypes.RecordPath:dtinfospath, FixParamTypes.RecordFDTType:f_type,
    #                    FixParamTypes.RecordFMDTType:fm_type
    #                    }

    fixdataparams = { #FixProcTypes.DTList:[fftime.get_time_from_datetime_for_single_pre_mul_obs, dtlistparams],
                     FixProcTypes.FileList:[ffinfos.get_fix_path_list_last, filelistparams],
                     FixProcTypes.ReadData:[frdata.read_gribdata_from_grib2_with_pygrib_single_file_seqnum, readdataparams],
                     #FixProcTypes.MulData:[fmuldata.verify_sta_tmx_pre_mul_obs, muldataparams],
                     FixProcTypes.WriteData:[fwdata.save_gribs_to_m4, writedataparams]#,
                     #FixProcTypes.RecordData:[frecdata.save_dtinfos, recorddataparams]
                     }

    fdata.fix_data_muldst_notime(fixdataparams)

def set_params(params, workdir):
    try:
        global fix_dict
        if FixParamTypes.SDict in params:
            fix_dict = params[FixParamTypes.SDict]
        else:
            fix_dict = None

        global fix_fn_fmt
        if FixParamTypes.SFnFmt in params:
            fix_fn_fmt = params[FixParamTypes.SFnFmt]
        else:
            fix_fn_fmt = None
            
        global s_fhs
        if FixParamTypes.SFHS in params:
            s_fhs = params[FixParamTypes.SFHS]
        else:
            s_fhs = None
            
        global s_seq
        if FixParamTypes.SSeq in params:
            s_seq = params[FixParamTypes.SSeq]
        else:
            s_seq = None
            
        global save_dict
        if FixParamTypes.DDict in params:
            save_dict = params[FixParamTypes.DDict]
        else:
            save_dict = None
            
        global save_fn_fmt
        if FixParamTypes.DFnFmt in params:
            save_fn_fmt = params[FixParamTypes.DFnFmt]
        else:
            save_fn_fmt = None
            
        global save_fhs
        if FixParamTypes.DFHS in params:
            save_fhs = params[FixParamTypes.DFHS]
        else:
            save_fhs = None
            
        global d_seq
        if FixParamTypes.DSeq in params:
            d_seq = params[FixParamTypes.DSeq]
        else:
            d_seq = None
            
        global d_seq_fmt
        if FixParamTypes.DSeqFmt in params:
            d_seq_fmt = params[FixParamTypes.DSeqFmt]
        else:
            d_seq_fmt = None
            
        #global log_file_name
        #if FixParamTypes.CfgFilePath in params:
        #    log_file_name = params[FixParamTypes.CfgFilePath]

        global fix_stime
        if FixParamTypes.STime in params:
            fix_stime = params[FixParamTypes.STime]
            
        global fix_etime
        if FixParamTypes.ETime in params:
            fix_etime = params[FixParamTypes.ETime]

        global dtinfospath
        if FixParamTypes.RecordPath in params:
           dtinfospath = params[FixParamTypes.RecordPath]
           if dtinfospath is None or len(dtinfospath) == 0:
               raise Exception('RecordPath error')

           dtinfospath = public.get_path_infos(dtinfospath, workdir=workdir)[1]
        else:
            dtinfospath = None

        global s_f_delta
        if FixParamTypes.SFDelta in params:
            s_f_delta = params[FixParamTypes.SFDelta]
        else:
            s_f_delta = None
            
        global s_fhs_delta
        if FixParamTypes.SFhsDelta in params:
            s_fhs_delta = params[FixParamTypes.SFhsDelta]
        else:
            s_fhs_delta = None
            
        global d_fhs_delta
        if FixParamTypes.DFhsDelta in params:
            d_fhs_delta = params[FixParamTypes.DFhsDelta]
        else:
            d_fhs_delta = None

        return True
    except Exception as data:
        print(str(data))
        return False

if __name__ == '__main__':
    workdir = os.path.dirname(__file__)
    
    logdir, logfile = public.get_path_infos(None, workdir=workdir, defaultdir=log_file_dir, defaultfn=log_file_name)

    init_log(logfile)
    
    progparams = public.parse_prog_params()
    if progparams is None:
        #print('program params error')
        LogLib.logger.error('program params error')
        uninit_log()
        sys.exit(1)

    if FixParamTypes.LogFilePath in progparams:
        uninit_log()

        logdir, logfile = public.get_path_infos(progparams[FixParamTypes.LogFilePath], workdir=workdir, defaultdir=log_file_dir, defaultfn=log_file_name)

        init_log(logfile)

    cfgfiledir = None
    cfgfilepath = None
    if FixParamTypes.CfgFilePath in progparams:
        cfgfiledir, cfgfilepath = public.get_path_infos(progparams[FixParamTypes.CfgFilePath], workdir=workdir, defaultdir=cfg_file_dir, defaultfn=cfg_file_name)
    else:
        cfgfiledir, cfgfilepath = public.get_path_infos(None, workdir=workdir, defaultdir=cfg_file_dir, defaultfn=cfg_file_name)

    cfgobj = Config()
    if cfgobj.parse(cfgfilepath) is None:
        #print('config ini params error')
        LogLib.logger.error('config ini params error')
        uninit_log()
        sys.exit(1)

    for i in range(len(cfgobj.subcfgobjlist)):
        curparams = {}
        cfgobj.setparams(curparams, i)

        curparams.update(progparams)

        if not set_params(curparams, workdir):
            #print('set_params config error')
            LogLib.logger.error('set_params config error')
            uninit_log()
            sys.exit(1)

        '''
        fix_dict = fix_dicts[i]
        fix_fn_fmt = fix_fn_fmts[i]
        
        s_fhs = s_fhs_s[i]

        s_seq = s_seq_s[i]
        d_seq = d_seq_s[i]

        s_f_delta = s_f_deltas[i]

        s_fhs_delta = s_fhs_deltas[i]
        '''

        proc()
    
    uninit_log()

    print('done')
