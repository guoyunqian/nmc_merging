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

#日志对象
loglib = LogLibMul()
#日志文件存储目录
log_file_dir = 'logfiles'
#日志文件的文件名
log_file_name = 'nmc_merging.log'

#配置文件存储目录
cfg_file_dir = 'config'
#日志文件的文件名
cfg_file_name = 'cfg_main.ini'

#初始化日志
def init_log(logfiles, loglib):
    loglib.init(logfiles.keys())
    loglib.addTimedRotatingFileHandler(logfiles)

    levels = {}
    for k,v in logfiles.items():
        levels[k] = logging.DEBUG

    loglib.setLevel(levels)
    
def need_backup(exist_seq, need_seq, seq_delta=0):
    need_seq_set = set(need_seq)
    exist_seq_set = set(exist_seq)
    if seq_delta < 0:
        exist_seq_set.update(range(1, -seq_delta+1))

    return (len(need_seq_set.difference(exist_seq_set)) > 0)

#读数据
def read_data(dt, srccfg, cur_d_seq, ffinfos, frdata, savedt, src_datas, delta_t, logger):
    logger.info('read_data start')

    read_data_list = []
    cur_src_datas = {}
    cur_total_seq = set([])

    is_complete = False

    if srccfg[FixParamTypes.CfgObj].srclist is None:
        logger.error('read_data no file %s' % (str(srccfg)))
        return False

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
            
        seq_delta = int((savedt - read_dt).total_seconds() / 3600)
        
        grdlist = public.get_grid_from_grib_file(frdata, fixfullpath, read_dt, list(map(lambda x:x+seq_delta, srccfg[FixParamTypes.DSeq])),
                                                 gribrst=False, seq_key_is_num=True, logger=logger)
                                                 #seq_field=GribTypes.stepRange, 
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

            if not cfgobj[FixParamTypes.ComPreferred]:
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

def get_save_paths(ffinfos, dpath, dst_fullpaths, savecfginfos, savedt, logger):
    logger.info('get_save_paths start')

    params = { FixParamTypes.DT:savedt, FixParamTypes.DDict:dpath,
              FixParamTypes.DFnFmt:savecfginfos[FixParamTypes.DFnFmt], FixParamTypes.DSeq:savecfginfos[FixParamTypes.DSeq]
              }

    saveinfos = ffinfos.get_save_path(params)

    if saveinfos is None:
        logger.info('get_save_paths error')

        return False

    dst_fullpaths.update(saveinfos)

    logger.info('get_save_paths over')

    return True

def write_data_m4(cfgobj, fwrite, dst_fullpaths, savedt, dst_datas, logger):
    logger.info('write_data_m4 start')

    #保存
    wparams = {}
    wparams[FixParamTypes.DT] = savedt

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
            logger.info('write_data_m4 over %s' % (dst_fullpaths[seqnum]))
        else:
            logger.error('write_data_m4 error %s' % (dst_fullpaths[seqnum]))

    logger.info('write_data_m4 over')
    
def write_data_m11(cfgobj, fwrite, dst_fullpaths, savedt, dst_datas, logger):
    logger.info('write_data_m11 start')

    #保存
    wparams = {}
    wparams[FixParamTypes.DT] = savedt

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
        wparams[FixParamTypes.GridData] = griddata.values.reshape(2*wparams[FixParamTypes.NLat], wparams[FixParamTypes.NLon])
        wparams[FixParamTypes.DFullPath] = dst_fullpaths[seqnum]
        wparams[FixParamTypes.SeqNum] = seqnum

        if fwrite.save_griddata_to_m11_no_meb(wparams):
            logger.info('write_data_m11 over %s' % (dst_fullpaths[seqnum]))
        else:
            logger.error('write_data_m11 error %s' % (dst_fullpaths[seqnum]))

    logger.info('write_data_m11 over')
    
def write_data_bin(cfgobj, fwrite, dst_fullpaths, dst_datas, logger):
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

def proc(cfgobj, etime, delta_t, logger, loglib):
    ffinfos = FixFileInfos(logger)
    frdata = FixReadData(logger)
    fwrite = FixWriteData(logger)
    
    #global save_dt
    save_e_time = etime+datetime.timedelta(minutes=cfgobj.savecfginfos[FixParamTypes.DFhsDelta])
    #数据的起报时时间
    save_dt = public.get_dt_with_fhs(save_e_time, cfgobj.savecfginfos[FixParamTypes.DFHS], delta_t)

    minseqnum = int((etime.replace(minute=0, second=0, microsecond=0) - save_dt).total_seconds() / 3600)
    
    #从数据源中获取的数据，以多层字典形式存在，第一层key为配置文件中的section名字
    #value为以时效为key，xarray的格点数据为value的字典
    src_datas = {}

    #从数据源获得数据
    for srccfg in cfgobj.srccfglist:
        cur_d_seq = srccfg[FixParamTypes.DSeq] if minseqnum <= 0 else list(set(srccfg[FixParamTypes.DSeq]).difference(set(range(1, minseqnum+1))))

        read_data(etime, srccfg, cur_d_seq, ffinfos, frdata, save_dt, src_datas, delta_t, loglib.getlogger(srccfg[FixParamTypes.DatasName]))

    #经过处理后的需要保存的数据，以时效为key，xarray的格点数据为value的字典
    dst_datas = {}

    #处理数据
    for proccfg in cfgobj.proccfglist:
        pparams = procfunc.procfuncs.set_func_params(proccfg[FixParamTypes.FuncName], save_dt, proccfg, src_datas, cfgobj.savecfginfos, dst_datas, logger)
        procfunc.procfuncs.run_func(proccfg[FixParamTypes.FuncName], pparams, logger)
        
    #数据保存路径，以时效为key，路径为value的字典
    dst_fullpaths = {}

    #获取数据保存信息
    if not get_save_paths(ffinfos, cfgobj.savecfginfos[FixParamTypes.DDict], dst_fullpaths, cfgobj.savecfginfos, save_dt, logger):
        return

    #保存
    write_data_bin(cfgobj, fwrite, dst_fullpaths, dst_datas, logger)

    #是否保存m4
    if cfgobj.savecfginfos[FixParamTypes.SaveM4] == 1:
        dst_fullpaths.clear()
        #获取数据保存信息
        if not get_save_paths(ffinfos, cfgobj.savecfginfos[FixParamTypes.DDictM4], dst_fullpaths, cfgobj.savecfginfos, save_dt, logger):
            return

        #保存
        if cfgobj.savecfginfos[FixParamTypes.SaveType] == 1:
            write_data_m11(cfgobj, fwrite, dst_fullpaths, save_dt, dst_datas, logger)
        else:
            write_data_m4(cfgobj, fwrite, dst_fullpaths, save_dt, dst_datas, logger)

    #os.system(save_dt.strftime('bash /space/cmadaas/dpl/NWFD01/code/nwfd/m2grib/run.sh -n -d %Y%m%d-%Y%m%d -b %H'))
    if cfgobj.grib2cfginfos is not None and FixParamTypes.ExecFmt in cfgobj.grib2cfginfos:
        exec_fmt = cfgobj.grib2cfginfos[FixParamTypes.ExecFmt]
        if exec_fmt is not None:
            exec_cmd = public.get_path_with_replace(exec_fmt, dt=save_dt)
            logger.info('proc %s' % exec_cmd)
            os.system(exec_cmd)

if __name__ == '__main__':
    workdir = os.path.dirname(os.path.abspath(__file__))
    
    mainlogger = None

    logdir, logfile = public.get_path_infos(None, workdir=workdir, defaultdir=log_file_dir, defaultfn=log_file_name)

    init_log({ log_file_name:logfile }, loglib)
    mainlogger = loglib.getlogger(log_file_name)
    
    progparams = public.parse_prog_params()
    if progparams is None:
        print('program params error')
        mainlogger.error('program params error')
        sys.exit(1)

    if FixParamTypes.LogFilePath in progparams:
        loglib.uninit()

        logdir, logfile = public.get_path_infos(progparams[FixParamTypes.LogFilePath], workdir=workdir, defaultdir=log_file_dir, defaultfn=log_file_name)

        init_log({ log_file_name:logfile }, loglib)
        mainlogger = loglib.getlogger(log_file_name)

    cfgfiledir = None
    cfgfilepath = None
    if FixParamTypes.CfgFilePath in progparams:
        cfgfiledir, cfgfilepath = public.get_path_infos(progparams[FixParamTypes.CfgFilePath], workdir=workdir, defaultdir=cfg_file_dir, defaultfn=cfg_file_name)
    else:
        cfgfiledir, cfgfilepath = public.get_path_infos(None, workdir=workdir, defaultdir=cfg_file_dir, defaultfn=cfg_file_name)

    cfgobj = CfgMain(mainlogger)
    if cfgobj.parse(cfgfilepath) is None:
        #print('config ini params error')
        mainlogger.error('config ini params error')
        sys.exit(1)

    for srccfg in cfgobj.srccfglist:
        srclogdir, srclogfile = public.get_path_infos(srccfg[FixParamTypes.LogFilePath], workdir=logdir)
        init_log({ srccfg[FixParamTypes.DatasName]:srclogfile }, loglib)

    #如果没有参数，使用默认的fix_etime，否则使用参数运行程序
    #如果参数是一个时间段，默认往前找对应的起报时执行，否则按指定时间执行。
    if FixParamTypes.STime in progparams and FixParamTypes.ETime in progparams:
        if progparams[FixParamTypes.STime] is None:
            proc(cfgobj, fix_etime, delta_t, mainlogger, loglib)
        elif progparams[FixParamTypes.ETime] is None:
            fix_etime = progparams[FixParamTypes.STime]
            proc(cfgobj, fix_etime, delta_t, mainlogger, loglib)
        else:
            stime = progparams[FixParamTypes.STime]
            etime = progparams[FixParamTypes.ETime]
            etime = public.get_dt_with_fhs(etime, cfgobj.savecfginfos[FixParamTypes.DFHS], delta_t)
            while(stime <= etime):
                fix_etime = etime
                proc(cfgobj, fix_etime, delta_t, mainlogger, loglib)

                etime -= datetime.timedelta(minutes=delta_t)
                etime = public.get_dt_with_fhs(etime, cfgobj.savecfginfos[FixParamTypes.DFHS], delta_t)
    else:
        proc(cfgobj, fix_etime, delta_t, mainlogger, loglib)

    print('done')
