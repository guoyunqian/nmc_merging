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

from logmodule.loglibmul import *
from publictype.fixproctypes import FixProcTypes
from publictype.fixparamtypes import FixParamTypes
from publictype.fixfileTypes import FixFileTypes
from publictype.gribtypes import GribTypes
import public
from cfg_main import CfgMain
from cfg_srcdata import CfgSrcData

from framework.fixfileinfos import FixFileInfos
from framework.fixreaddata import FixReadData
from framework.fixwritedata import FixWriteData

import procfunc
import checkfunc

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
fix_etime = datetime.datetime.now()  #.replace(minute=0,second=0,microsecond=0)
#fix_stime = fix_etime - datetime.timedelta(hours=12)

#获取时间列表时，每个时间的最小间隔
delta_t = 60

#确定文件的时间差
s_f_delta = None

#确定起报时的时间差
s_fhs_delta = None

d_fhs_delta = int(2.5*60)

#源文件目录
fix_dict = None

#目标文件目录
save_dict = None

#源文件名
fix_fn_fmt = None

#目标文件名
save_fn_fmt = None

#获取时间时，需要选择的小时，使用range获得，或者直接用list指定
s_fhs = None

save_fhs = None

#预报时效
s_seq = None
d_seq = None

#时效格式
d_seq_fmt = None

#日志对象
loglib = None
#日志文件存储目录
log_file_dir = 'logfiles'
#日志文件的文件名
log_file_name = 'nmc_merging.log'

#配置文件存储目录
cfg_file_dir = 'config'
#日志文件的文件名
cfg_file_name = 'cfg_main.ini'

#从数据源中获取的数据，以多层字典形式存在，第一层key为配置文件中的section名字
#value为以时效为key，xarray的格点数据为value的字典
src_datas = {}

#{'data01':{ 1:xarray }}

#经过处理后的需要保存的数据，以时效为key，xarray的格点数据为value的字典
dst_datas = {}

#数据保存路径，以时效为key，路径为value的字典
#dst_fullpaths = {}

#数据的起报时时间
save_dt = None

#初始化日志
def init_log(logfiles):
    global loglib

    if loglib is None:
        loglib = LogLibMul()

    loglib.init(logfiles.keys())
    loglib.addTimedRotatingFileHandler(logfiles)

    levels = {}
    for k,v in logfiles.items():
        levels[k] = logging.DEBUG

    loglib.setLevel(levels)
    
'''
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
    '''


def need_backup(exist_seq, need_seq, seq_delta=0):
    need_seq_set = set(need_seq)
    exist_seq_set = set(exist_seq)
    if seq_delta < 0:
        exist_seq_set.update(range(1, -seq_delta+1))

    return (len(need_seq_set.difference(exist_seq_set)) > 0)

#读数据
def read_data(dt, srccfg, cur_d_seq, ffinfos, frdata):
    logger = loglib.getlogger(srccfg[FixParamTypes.DatasName])

    logger.info('read_data start')

    read_data_list = []
    cur_src_datas = {}
    cur_total_seq = set([])

    is_complete = False

    for bobj, fhs_delta in srccfg[FixParamTypes.CfgObj].srclist:
        cfgobj = bobj.srcinfos

        read_e_dt = dt + datetime.timedelta(minutes=cfgobj[FixParamTypes.SFhsDelta])
        read_dt = public.get_dt_with_fhs(read_e_dt, cfgobj[FixParamTypes.SFHS], delta_t, fhs_delta=fhs_delta)

        flistparams = { FixParamTypes.DT:read_dt, FixParamTypes.SDict:cfgobj[FixParamTypes.SDict],
                       FixParamTypes.SFnFmt:cfgobj[FixParamTypes.SFnFmt], FixParamTypes.SFDelta:cfgobj[FixParamTypes.SFDelta],
                       FixParamTypes.CurLogger:logger
                       }

        fixfullpath = ffinfos.get_fix_path_list_last(flistparams)
        if fixfullpath == None:
            logger.warning('read_data no file %s' % (str(flistparams)))
            continue
            
        seq_delta = int((save_dt - read_dt).total_seconds() / 3600)
        
        grdlist = public.get_grid_from_grib_file(frdata, fixfullpath, read_dt, list(map(lambda x:x+seq_delta, srccfg[FixParamTypes.DSeq])),
                                                 seq_field=GribTypes.stepRange, gribrst=False, seq_key_is_num=True, logger=logger)
        if grdlist is None:
            logger.error('read_data read file error %s' % (fixfullpath))
            return False
        
        keys = list(grdlist.keys())
        for k in keys:
            for checkcfg in bobj.checkcfglist:
                checkparams = {}
                checkfunc.checkfuncs.set_func_params(checkcfg[FixParamTypes.FuncName], checkparams, grdlist[k], checkcfg, logger)
                if checkfunc.checkfuncs.run_func(checkcfg[FixParamTypes.FuncName], checkparams, logger):
                    del grdlist[k]
                    break

        for k,v in grdlist.items():
            cur_src_datas[k-seq_delta] = v
            cur_total_seq.add(k-seq_delta)

        if need_backup(cur_src_datas.keys(), cur_d_seq, seq_delta):
            read_data_list.append(grdlist)

            if not bobj[FixParamTypes.ComPreferred]:
                if not need_backup(cur_total_seq, cur_d_seq, seq_delta):
                    break
        else:
            is_complete = True
            break

    if is_complete:
        src_datas[srccfg[FixParamTypes.DatasName]] = cur_src_datas
    else:
        read_data_list.append(cur_src_datas)

        rsts = {}
        need_seq_set = set(cur_d_seq)
        for datas in read_data_list:
            exist_seq_set = set(list(rsts.keys()))
            for s in need_seq_set.difference(exist_seq_set):
                if s in datas:
                    rsts[s] = datas[s]

        src_datas[srccfg[FixParamTypes.DatasName]] = rsts
        
    logger.info('read_data over')

    return True

def get_save_paths(ffinfos, dpath, dst_fullpaths):
    logger = loglib.getlogger(log_file_name)

    logger.info('get_save_paths start')

    params = { FixParamTypes.DT:save_dt, FixParamTypes.DDict:dpath,
              FixParamTypes.DFnFmt:cfgobj.savecfginfos[FixParamTypes.DFnFmt], FixParamTypes.DSeq:cfgobj.savecfginfos[FixParamTypes.DSeq]
              }

    saveinfos = ffinfos.get_save_path(params)

    if saveinfos is None:
        logger.info('get_save_paths error')

        return False

    dst_fullpaths.update(saveinfos)

    logger.info('get_save_paths over')

    return True

def write_data_m4(cfgobj, fwrite, dst_fullpaths):
    logger = loglib.getlogger(log_file_name)

    logger.info('write_data_m4 start')

    #保存
    wparams = {}
    wparams[FixParamTypes.DT] = save_dt

    wparams[FixParamTypes.NLon] = cfgobj.savecfginfos[FixParamTypes.NLon]
    wparams[FixParamTypes.NLat] = cfgobj.savecfginfos[FixParamTypes.NLat]
    wparams[FixParamTypes.SLon] = cfgobj.savecfginfos[FixParamTypes.SLon]
    wparams[FixParamTypes.SLat] = cfgobj.savecfginfos[FixParamTypes.SLat]
    wparams[FixParamTypes.ELon] = cfgobj.savecfginfos[FixParamTypes.ELon]
    wparams[FixParamTypes.ELat] = cfgobj.savecfginfos[FixParamTypes.ELat]
    wparams[FixParamTypes.DLon] = cfgobj.savecfginfos[FixParamTypes.DLon]
    wparams[FixParamTypes.DLat] = cfgobj.savecfginfos[FixParamTypes.DLat]

    wparams[FixParamTypes.Decimals] = cfgobj.savecfginfos[FixParamTypes.Decimals]
    wparams[FixParamTypes.ScaleDecimals] = cfgobj.savecfginfos[FixParamTypes.ScaleDecimals]

    for seqnum,griddata in dst_datas.items():
        wparams[FixParamTypes.GridData] = griddata.values.reshape(wparams[FixParamTypes.NLat], wparams[FixParamTypes.NLon])
        wparams[FixParamTypes.DFullPath] = dst_fullpaths[seqnum]
        wparams[FixParamTypes.SeqNum] = seqnum

        if fwrite.save_griddata_to_m4_no_meb(wparams):
            logger.info('save griddata file over %s' % (dst_fullpaths[seqnum]))
        else:
            logger.error('save griddata file file error %s' % (dst_fullpaths[seqnum]))

    logger.info('write_data_m4 over')
    
def write_data_bin(cfgobj, fwrite, dst_fullpaths):
    logger = loglib.getlogger(log_file_name)

    logger.info('write_data_bin start')

    #保存
    wparams = {}

    for seqnum,griddata in dst_datas.items():
        wparams[FixParamTypes.GridData] = griddata.values
        wparams[FixParamTypes.DFullPath] = dst_fullpaths[seqnum]

        if fwrite.save_data_to_bin_with_struct(wparams):
            logger.info('save griddata file over %s' % (dst_fullpaths[seqnum]))
        else:
            logger.error('save griddata file file error %s' % (dst_fullpaths[seqnum]))

    logger.info('write_data_bin over')

def proc(cfgobj):
    logger = loglib.getlogger(log_file_name)
    
    ffinfos = FixFileInfos(logger)
    frdata = FixReadData(logger)
    fwrite = FixWriteData(logger)
    
    global save_dt
    save_e_time = fix_etime+datetime.timedelta(minutes=cfgobj.savecfginfos[FixParamTypes.DFhsDelta])
    save_dt = public.get_dt_with_fhs(save_e_time, cfgobj.savecfginfos[FixParamTypes.DFHS], delta_t)

    minseqnum = int((fix_etime.replace(minute=0, second=0, microsecond=0) - save_dt).total_seconds() / 3600)

    #从数据源获得数据
    for srccfg in cfgobj.srccfglist:
        cur_d_seq = srccfg[FixParamTypes.DSeq] if minseqnum <= 0 else list(set(srccfg[FixParamTypes.DSeq]).difference(set(range(1, minseqnum+1))))

        read_data(fix_etime, srccfg, cur_d_seq, ffinfos, frdata)

    #处理数据
    for proccfg in cfgobj.proccfglist:
        pparams = procfunc.procfuncs.set_func_params(proccfg[FixParamTypes.FuncName], save_dt, proccfg, src_datas, cfgobj.savecfginfos, dst_datas, logger)
        procfunc.procfuncs.run_func(proccfg[FixParamTypes.FuncName], pparams, logger)
        
    dst_fullpaths = {}
    #获取数据保存信息
    if not get_save_paths(ffinfos, cfgobj.savecfginfos[FixParamTypes.DDict], dst_fullpaths):
        return

    #保存
    write_data_bin(cfgobj, fwrite, dst_fullpaths)

    #是否保存m4
    if cfgobj.savecfginfos[FixParamTypes.SaveM4] == 1:
        dst_fullpaths.clear()
        #获取数据保存信息
        if not get_save_paths(ffinfos, cfgobj.savecfginfos[FixParamTypes.DDictM4], dst_fullpaths):
            return

        #保存
        write_data_m4(cfgobj, fwrite, dst_fullpaths)

    os.system(save_dt.strftime('bash /space/cmadaas/dpl/NWFD01/code/nwfd/m2grib/run.sh -n -d %Y%m%d-%Y%m%d -b %H'))

if __name__ == '__main__':
    workdir = os.path.dirname(os.path.abspath(__file__))
    
    logdir, logfile = public.get_path_infos(None, workdir=workdir, defaultdir=log_file_dir, defaultfn=log_file_name)

    init_log({ log_file_name:logfile })
    
    progparams = public.parse_prog_params()
    if progparams is None:
        print('program params error')
        loglib.getlogger(log_file_name).error('program params error')
        sys.exit(1)

    if FixParamTypes.LogFilePath in progparams:
        loglib.uninit()

        logdir, logfile = public.get_path_infos(progparams[FixParamTypes.LogFilePath], workdir=workdir, defaultdir=log_file_dir, defaultfn=log_file_name)

        init_log({ log_file_name:logfile })

    cfgfiledir = None
    cfgfilepath = None
    if FixParamTypes.CfgFilePath in progparams:
        cfgfiledir, cfgfilepath = public.get_path_infos(progparams[FixParamTypes.CfgFilePath], workdir=workdir, defaultdir=cfg_file_dir, defaultfn=cfg_file_name)
    else:
        cfgfiledir, cfgfilepath = public.get_path_infos(None, workdir=workdir, defaultdir=cfg_file_dir, defaultfn=cfg_file_name)

    cfgobj = CfgMain(loglib.getlogger(log_file_name))
    if cfgobj.parse(cfgfilepath) is None:
        #print('config ini params error')
        loglib.getlogger(log_file_name).logger.error('config ini params error')
        sys.exit(1)

    for srccfg in cfgobj.srccfglist:
        srclogdir, srclogfile = public.get_path_infos(srccfg[FixParamTypes.LogFilePath], workdir=logdir)
        init_log({ srccfg[FixParamTypes.DatasName]:srclogfile })

    if FixParamTypes.STime in progparams and FixParamTypes.ETime in progparams:
        if progparams[FixParamTypes.STime] is None:
            proc(cfgobj)
        elif progparams[FixParamTypes.ETime] is None:
            fix_etime = progparams[FixParamTypes.STime]
            proc(cfgobj)
        else:
            stime = progparams[FixParamTypes.STime]
            etime = progparams[FixParamTypes.ETime]
            while(stime <= etime):
                fix_etime = etime
                proc(cfgobj)

                etime -= datetime.timedelta(minutes=delta_t*12)
    else:
        proc(cfgobj)

    print('done')
