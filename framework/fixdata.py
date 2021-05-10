#!/usr/bin/python
# -*- coding: utf-8 -*-
#Filename: fixdata.py

'''
Created on Aug 21, 2020

@author: anduin
'''

import os
import datetime

from logmodule.loglib import *
from publictype.fixproctypes import FixProcTypes
from publictype.fixparamtypes import FixParamTypes

class FixData(object):
    def set_read_params_saveinfos_mul_dst(self, readparams, savefullpathinfo):
        if savefullpathinfo[0][2] is not None:
            readparams[FixParamTypes.DT] = savefullpathinfo[0][2]
        
    def set_read_params_saveinfos(self, readparams, savefullpathinfo):
        if savefullpathinfo[1] is not None:
            readparams[FixParamTypes.SeqNum] = savefullpathinfo[1]

        if savefullpathinfo[2] is not None:
            readparams[FixParamTypes.DT] = savefullpathinfo[2]
        
    def set_modify_params_saveinfos(self, mparams, savefullpathinfo):
        if savefullpathinfo[1] is not None:
            mparams[FixParamTypes.SeqNum] = savefullpathinfo[1]

        if savefullpathinfo[2] is not None:
            mparams[FixParamTypes.DT] = savefullpathinfo[2]

    def set_write_params_saveinfos(self, wparams, savefullpathinfo):
        if savefullpathinfo[1] is not None:
            wparams[FixParamTypes.SeqNum] = savefullpathinfo[1]

        if savefullpathinfo[2] is not None:
            wparams[FixParamTypes.DT] = savefullpathinfo[2]

    def set_write_params_grib_infos(self, wparams, infos):
        wparams.update(infos[0])
        wparams[FixParamTypes.DT] = infos[1]

    def fix_data(self, params, quit_when_error=False):
        try:
            LogLib.logger.info('FixData fix_data start')
            dt_list = params[FixProcTypes.DTList][0](params[FixProcTypes.DTList][1])
            LogLib.logger.debug('FixData fix_data dt_list:%s' % str(dt_list))

            for dt in dt_list:
                try:
                    LogLib.logger.info('FixData fix_data process datetime start %s' % (dt.strftime('%Y-%m-%d %H:%M:%S')))

                    flistparams = params[FixProcTypes.FileList][1]
                    flistparams[FixParamTypes.DT] = dt

                    fixfullpaths = params[FixProcTypes.FileList][0](flistparams)
                    if fixfullpaths == None or len(fixfullpaths) == 0:
                        LogLib.logger.warning('FixData fix_data process datetime no file %s' % (dt.strftime('%Y-%m-%d %H:%M:%S')))
                        continue

                    LogLib.logger.debug('FixData fix_data process fixfullpaths %s:%s' % (dt.strftime('%Y-%m-%d %H:%M:%S'), str(fixfullpaths)))

                    for (fixfullpath, savefullpathinfo) in fixfullpaths.items():
                        LogLib.logger.info('FixData fix_data process file start %s' % (fixfullpath))

                        readparams = params[FixProcTypes.ReadData][1]
                        readparams[FixParamTypes.SFullPath] = fixfullpath
                        if FixParamTypes.SetParamsProc in readparams:
                            readparams[FixParamTypes.SetParamsProc](readparams, savefullpathinfo)

                        grd = params[FixProcTypes.ReadData][0](readparams)
                        if grd is None:
                            LogLib.logger.error('FixData fix_data read file error %s' % (fixfullpath))
                            if quit_when_error:
                                return
                            else:
                                continue

                        have_err = False
                        for procobj in params[FixProcTypes.ModifyData]:
                            mparams = procobj[1]
                            mparams[FixParamTypes.GridData] = grd
                            if FixParamTypes.SetParamsProc in mparams:
                                mparams[FixParamTypes.SetParamsProc](mparams, savefullpathinfo)

                            grd = procobj[0](mparams)
                            if grd is None:
                                LogLib.logger.error('FixData fix_data modify file error %s %s' % (fixfullpath, str(procobj)))
                                have_err = True
                                break

                        if have_err:
                            if quit_when_error:
                                return
                            else:
                                continue

                        if type(savefullpathinfo) is str or type(savefullpathinfo) is list and type(savefullpathinfo[0]) is str:
                            savefullpath = savefullpathinfo if type(savefullpathinfo) is str else savefullpathinfo[0]
                        
                            wparams = params[FixProcTypes.WriteData][1]
                            wparams[FixParamTypes.GridData] = grd
                            wparams[FixParamTypes.DFullPath] = savefullpath
                            if FixParamTypes.SetParamsProc in wparams:
                                wparams[FixParamTypes.SetParamsProc](wparams, savefullpathinfo)

                            if params[FixProcTypes.WriteData][0](wparams):
                                LogLib.logger.info('FixData fix_data process file over %s %s' % (fixfullpath, savefullpath))
                            else:
                                LogLib.logger.error('FixData fix_data write file error %s %s' % (fixfullpath, savefullpath))
                                if quit_when_error:
                                    return
                                else:
                                    continue
                        #mul dst
                        elif type(savefullpathinfo) is list and type(savefullpathinfo[0]) is list:
                            for info in savefullpathinfo:
                                savefullpath = info[0]
                        
                                wparams = params[FixProcTypes.WriteData][1]
                                wparams[FixParamTypes.GridData] = grd
                                wparams[FixParamTypes.DFullPath] = savefullpath
                                if FixParamTypes.SetParamsProc in wparams:
                                    wparams[FixParamTypes.SetParamsProc](wparams, info)

                                if not params[FixProcTypes.WriteData][0](wparams):
                                    LogLib.logger.error('FixData fix_data write file error %s %s' % (fixfullpath, savefullpath))
                                    if quit_when_error:
                                        return
                                    else:
                                        continue
                                    
                            LogLib.logger.info('FixData fix_data process file over %s %s' % (fixfullpath, savefullpath))
                        else:
                            raise Exception('not support savefullpathinfo')

                    LogLib.logger.info('FixData fix_data process datetime over %s' % (dt.strftime('%Y-%m-%d %H:%M:%S')))
                except Exception as dtdata:
                    LogLib.logger.error('FixData fix_data process error %s %s' % (dt.strftime('%Y-%m-%d %H:%M:%S'), str(dtdata)))
                    raise dtdata

            LogLib.logger.info('FixData fix_data over')
        except Exception as data:
            LogLib.logger.error('FixData fix_data except %s' % (str(data)))
            
    def set_modify_params_savefullpath(self, mparams, savefullpath):
        import os
        dir,fname = os.path.split(savefullpath)
        mparams[FixParamTypes.FileName] = fname

	#一次确定出所有时间点需要的源文件和目标文件全路径
    def fix_data_with_dts_fname(self, params, quit_when_error=False):
        try:
            LogLib.logger.info('FixData fix_data_with_dts_fname start')
            dt_list = []
            if FixProcTypes.DTList in params:
                dt_list = params[FixProcTypes.DTList][0](params[FixProcTypes.DTList][1])
            LogLib.logger.debug('FixData fix_data_with_dts_fname dt_list:%s' % str(dt_list))

            flistparams = params[FixProcTypes.FileList][1]
            flistparams[FixParamTypes.DTS] = dt_list

            fixfullpaths = params[FixProcTypes.FileList][0](flistparams)
            if fixfullpaths == None or len(fixfullpaths) == 0:
                LogLib.logger.warning('FixData fix_data_with_dts_fname process datetime no file %s' % (str(flistparams)))
                return

            LogLib.logger.debug('FixData fix_data_with_dts_fname process fixfullpaths %s' % (str(fixfullpaths)))

            for (fixfullpath, savefullpath) in fixfullpaths.items():
                LogLib.logger.info('FixData fix_data_with_dts_fname process file start %s %s' % (fixfullpath, savefullpath))

                readparams = params[FixProcTypes.ReadData][1]
                readparams[FixParamTypes.SFullPath] = fixfullpath
                grd = params[FixProcTypes.ReadData][0](readparams)
                if grd is None:
                    LogLib.logger.error('FixData fix_data_with_dts_fname read file error %s %s' % (fixfullpath, savefullpath))
                    if quit_when_error:
                        return
                    else:
                        continue

                have_err = False
                for procobj in params[FixProcTypes.ModifyData]:
                    mparams = procobj[1]
                    mparams[FixParamTypes.GridData] = grd

                    
                    if FixParamTypes.SetParamsProc in mparams:
                        mparams[FixParamTypes.SetParamsProc](mparams, savefullpath)

                    grd = procobj[0](mparams)
                    if grd is None:
                        LogLib.logger.error('FixData fix_data_with_dts_fname modify file error %s %s' % (fixfullpath, str(procobj)))
                        have_err = True
                        break

                if have_err:
                    if quit_when_error:
                        return
                    else:
                        continue

                wparams = params[FixProcTypes.WriteData][1]
                wparams[FixParamTypes.GridData] = grd
                wparams[FixParamTypes.DFullPath] = savefullpath

                if params[FixProcTypes.WriteData][0](wparams):
                    LogLib.logger.info('FixData fix_data_with_dts_fname process file over %s %s' % (fixfullpath, savefullpath))
                else:
                    LogLib.logger.error('FixData fix_data_with_dts_fname write file error %s %s' % (fixfullpath, savefullpath))
                    
                    if quit_when_error:
                        return
                    else:
                        continue
            
            LogLib.logger.info('FixData fix_data_with_dts_fname over')
        except Exception as data:
            LogLib.logger.error('FixData fix_data_with_dts_fname except %s' % (str(data)))
            
    #一次确定出所有时间点需要的源文件和目标文件全路径
    def fix_data_with_dts(self, params, quit_when_error=False):
        try:
            LogLib.logger.info('FixData fix_data_with_dts start')
            dt_list = params[FixProcTypes.DTList][0](params[FixProcTypes.DTList][1])
            LogLib.logger.debug('FixData fix_data_with_dts dt_list:%s' % str(dt_list))

            flistparams = params[FixProcTypes.FileList][1]
            flistparams[FixParamTypes.DTS] = dt_list

            fixfullpaths = params[FixProcTypes.FileList][0](flistparams)
            if fixfullpaths == None or len(fixfullpaths) == 0:
                LogLib.logger.warning('FixData fix_data_with_dts process datetime no file %s' % (str(flistparams)))
                return

            LogLib.logger.debug('FixData fix_data_with_dts process fixfullpaths %s' % (str(fixfullpaths)))

            for (dt, savefullpath) in fixfullpaths.items():
                LogLib.logger.info('FixData fix_data_with_dts process file start %s %s' % (str(dt), savefullpath))

                readparams = params[FixProcTypes.ReadData][1]
                readparams[FixParamTypes.DT] = dt
                grd = params[FixProcTypes.ReadData][0](readparams)
                if grd is None:
                    LogLib.logger.error('FixData fix_data_with_dts read file error %s %s' % (str(dt), savefullpath))
                    if quit_when_error:
                        return
                    else:
                        continue

                have_err = False
                for procobj in params[FixProcTypes.ModifyData]:
                    mparams = procobj[1]
                    mparams[FixParamTypes.GridData] = grd

                    grd = procobj[0](mparams)
                    if grd is None:
                        LogLib.logger.error('FixData fix_data_with_dts modify file error %s %s' % (str(dt), str(procobj)))
                        have_err = True
                        break

                if have_err:
                    if quit_when_error:
                        return
                    else:
                        continue

                wparams = params[FixProcTypes.WriteData][1]
                wparams[FixParamTypes.GridData] = grd
                wparams[FixParamTypes.DT] = dt
                if type(savefullpath) is str:
                    wparams[FixParamTypes.DFullPath] = savefullpath
                else:
                    wparams[FixParamTypes.DFullPaths] = savefullpath

                if params[FixProcTypes.WriteData][0](wparams):
                    LogLib.logger.info('FixData fix_data_with_dts process file over %s %s' % (str(dt), savefullpath))
                else:
                    LogLib.logger.error('FixData fix_data_with_dts write file error %s %s' % (str(dt), savefullpath))
                    if quit_when_error:
                        return
                    else:
                        continue
            
            LogLib.logger.info('FixData fix_data_with_dts over')
        except Exception as data:
            LogLib.logger.error('FixData fix_data_with_dts except %s' % (str(data)))
            
    def set_read_params_stainfos(self, readparams, sta_code):
        readparams[FixParamTypes.DT] = dt
        readparams[FixParamTypes.StaID] = readparams[FixParamTypes.StaInfos][sta_code]['sat']
        readparams[FixParamTypes.SLon] = readparams[FixParamTypes.StaInfos][sta_code]['lon']
        readparams[FixParamTypes.SLat] = readparams[FixParamTypes.StaInfos][sta_code]['lat']

    def modify_data_time(self, grd, dt):
        grd['time'] = dt

    def sum_data(self, params, quit_when_error=False):
        try:
            LogLib.logger.info('FixData sum_data start')
            dt_list = params[FixProcTypes.DTList][0](params[FixProcTypes.DTList][1])
            LogLib.logger.debug('FixData sum_data dt_list:%s' % str(dt_list))

            for dt in dt_list:
                try:
                    LogLib.logger.info('FixData sum_data process datetime start %s' % (dt.strftime('%Y-%m-%d %H:%M:%S')))

                    flistparams = params[FixProcTypes.FileList][1]
                    flistparams[FixParamTypes.DT] = dt

                    savefullpath, fixfullpaths = params[FixProcTypes.FileList][0](flistparams)
                    if savefullpath == '' or len(fixfullpaths) == 0:
                        LogLib.logger.warning('FixData sum_data process datetime no file %s' % (dt.strftime('%Y-%m-%d %H:%M:%S')))
                        continue

                    LogLib.logger.debug('FixData sum_data process fixfullpaths %s:%s' % (dt.strftime('%Y-%m-%d %H:%M:%S'), str(fixfullpaths)))

                    have_err = False
                    grdlist = []
                    for fixfullpath, sta_code in fixfullpaths:
                        LogLib.logger.info('FixData sum_data process file start %s' % (fixfullpath))

                        readparams = params[FixProcTypes.ReadData][1]
                        readparams[FixParamTypes.SFullPath] = fixfullpath
                        if FixParamTypes.SetParamsProc in readparams:
                            readparams[FixParamTypes.SetParamsProc](readparams, sta_code)

                        grd = params[FixProcTypes.ReadData][0](readparams)
                        if grd is None:
                            LogLib.logger.error('FixData sum_data read file error %s' % (fixfullpath))
                            have_err = True
                            break

                        for procobj in params[FixProcTypes.ModifyData]:
                            mparams = procobj[1]
                            mparams[FixParamTypes.GridData] = grd

                            grd = procobj[0](mparams)
                            if grd is None:
                                LogLib.logger.error('FixData sum_data modify file error %s %s' % (fixfullpath, str(procobj)))
                                have_err = True
                                break

                        if have_err:
                            break

                        grdlist.append(grd)

                    if have_err:
                        if quit_when_error:
                            return
                        else:
                            continue
                        
                    sumgrd = None

                    mulparams = params[FixProcTypes.MulData][1]
                    mulparams[FixParamTypes.DstGridData] = sumgrd
                    mulparams[FixParamTypes.GridDataList] = grdlist
                    sumgrd = params[FixProcTypes.MulData][0](mulparams)
                    
                    if sumgrd is None:
                        LogLib.logger.error('FixData sum_data process sum error %s' % (dt.strftime('%Y-%m-%d %H:%M:%S')))
                        if quit_when_error:
                            return
                        else:
                            continue
                    
                    wparams = params[FixProcTypes.WriteData][1]
                    if FixParamTypes.Proc in wparams:
                        wparams[FixParamTypes.Proc](sumgrd, dt)
                        
                    wparams[FixParamTypes.GridData] = sumgrd
                    wparams[FixParamTypes.DFullPath] = savefullpath

                    if params[FixProcTypes.WriteData][0](wparams):
                        LogLib.logger.info('FixData sum_data process file over %s %s' % (dt.strftime('%Y-%m-%d %H:%M:%S'), savefullpath))
                    else:
                        LogLib.logger.error('FixData sum_data write file error %s %s' % (dt.strftime('%Y-%m-%d %H:%M:%S'), savefullpath))
                        if quit_when_error:
                            return
                        else:
                            continue
                            
                except Exception as dtdata:
                    LogLib.logger.error('FixData sum_data process error %s %s' % (dt.strftime('%Y-%m-%d %H:%M:%S'), str(dtdata)))
                    raise dtdata

            LogLib.logger.info('FixData sum_data over')
        except Exception as data:
            LogLib.logger.error('FixData sum_data except %s' % (str(data)))
            
    #针对一个文件中多个数据集的情况
    def sum_data_single_file(self, params, quit_when_error=False):
        try:
            LogLib.logger.info('FixData sum_data_single_file start')
            dt_list = params[FixProcTypes.DTList][0](params[FixProcTypes.DTList][1])
            LogLib.logger.debug('FixData sum_data_single_file dt_list:%s' % str(dt_list))

            for dt in dt_list:
                try:
                    LogLib.logger.info('FixData sum_data_single_file process datetime start %s' % (dt.strftime('%Y-%m-%d %H:%M:%S')))

                    flistparams = params[FixProcTypes.FileList][1]
                    flistparams[FixParamTypes.DT] = dt

                    savefullpath, fixfullpath, std = params[FixProcTypes.FileList][0](flistparams)
                    if savefullpath == '' or fixfullpath == '':
                        LogLib.logger.warning('FixData sum_data_single_file process datetime no file %s' % (dt.strftime('%Y-%m-%d %H:%M:%S')))
                        continue

                    LogLib.logger.debug('FixData sum_data_single_file process fixfullpath %s:%s' % (dt.strftime('%Y-%m-%d %H:%M:%S'), fixfullpath))
                    
                    fmtime = int(os.path.getmtime(fixfullpath))

                    readparams = params[FixProcTypes.ReadData][1]
                    readparams[FixParamTypes.SFullPath] = fixfullpath

                    grds = params[FixProcTypes.ReadData][0](readparams)
                    if grds is None:
                        LogLib.logger.error('FixData sum_data_single_file read file error %s' % (fixfullpath))
                        have_err = True
                        break

                    have_err = False
                    grdlist = []
                    for seq_str, grd in grds.items():
                        for procobj in params[FixProcTypes.ModifyData]:
                            mparams = procobj[1]
                            mparams[FixParamTypes.GridData] = grd

                            grd = procobj[0](mparams)
                            if grd is None:
                                LogLib.logger.error('FixData sum_data_single_file modify file error %s %s' % (seq_str, str(procobj)))
                                have_err = True
                                break

                        if have_err:
                            break

                        grdlist.append(grd)

                    if have_err:
                        if quit_when_error:
                            return
                        else:
                            continue
                        
                    sumgrd = None

                    mulparams = params[FixProcTypes.MulData][1]
                    mulparams[FixParamTypes.DstGridData] = sumgrd
                    mulparams[FixParamTypes.GridDataList] = grdlist
                    sumgrd = params[FixProcTypes.MulData][0](mulparams)
                    
                    if sumgrd is None:
                        LogLib.logger.error('FixData sum_data_single_file process sum error %s' % (dt.strftime('%Y-%m-%d %H:%M:%S')))
                        if quit_when_error:
                            return
                        else:
                            continue
                    
                    wparams = params[FixProcTypes.WriteData][1]
                    if FixParamTypes.SetParamsProc in wparams:
                        wparams[FixParamTypes.SetParamsProc](wparams, [sumgrd[0], std])
                        
                    wparams[FixParamTypes.GridData] = sumgrd[1]
                    wparams[FixParamTypes.DFullPath] = savefullpath

                    if params[FixProcTypes.WriteData][0](wparams):
                        LogLib.logger.info('FixData sum_data_single_file process file over %s %s' % (dt.strftime('%Y-%m-%d %H:%M:%S'), savefullpath))

                        if FixProcTypes.RecordData in params:
                            recparams = params[FixProcTypes.RecordData][1]

                            recparams[FixParamTypes.RecordData][recparams[FixParamTypes.RecordFDTType].value] = dt.strftime('%Y%m%d%H%M%S')
                            recparams[FixParamTypes.RecordData][recparams[FixParamTypes.RecordFMDTType].value] = fmtime

                            if params[FixProcTypes.RecordData][0](recparams):
                                LogLib.logger.info('FixData sum_data_single_file record over %s %s' % (dt.strftime('%Y-%m-%d %H:%M:%S'), savefullpath))
                            else:
                                LogLib.logger.error('FixData sum_data_single_file record error %s %s' % (dt.strftime('%Y-%m-%d %H:%M:%S'), savefullpath))
                                if quit_when_error:
                                    return
                                else:
                                    continue
                    else:
                        LogLib.logger.error('FixData sum_data_single_file write file error %s %s' % (dt.strftime('%Y-%m-%d %H:%M:%S'), savefullpath))
                        if quit_when_error:
                            return
                        else:
                            continue
                            
                except Exception as dtdata:
                    LogLib.logger.error('FixData sum_data_single_file process error %s %s' % (dt.strftime('%Y-%m-%d %H:%M:%S'), str(dtdata)))
                    raise dtdata

            LogLib.logger.info('FixData sum_data_single_file over')
        except Exception as data:
            LogLib.logger.error('FixData sum_data_single_file except %s' % (str(data)))
            
    #针对一个一个预报和多个时效的实况检验
    def check_data_single_pre_mul_obs(self, params, quit_when_error=False):
        try:
            LogLib.logger.info('FixData check_data_single_pre_mul_obs start')
            dt_list = params[FixProcTypes.DTList][0](params[FixProcTypes.DTList][1])
            LogLib.logger.debug('FixData check_data_single_pre_mul_obs dt_list:%s' % str(dt_list))

            flistparams = params[FixProcTypes.FileList][1]
            flistparams[FixParamTypes.DTS] = dt_list

            savefullpath, fixfullpaths = params[FixProcTypes.FileList][0](flistparams)
            if savefullpath == '' or len(fixfullpaths) == 0:
                LogLib.logger.warning('FixData check_data_single_pre_mul_obs process datetime no file %s' % (str(flistparams)))
                return

            sumgrd = None
            for fullpaths in fixfullpaths:
                try:
                    readparams = params[FixProcTypes.ReadData][1]
                    readparams[FixParamTypes.SFullPaths] = fullpaths

                    grds = params[FixProcTypes.ReadData][0](readparams)
                    if grds is None:
                        LogLib.logger.error('FixData check_data_single_pre_mul_obs read file error %s' % (str(readparams)))
                        return

                    mulparams = params[FixProcTypes.MulData][1]
                    if sumgrd is not None:
                        mulparams[FixParamTypes.DstGridData] = sumgrd
                    mulparams[FixParamTypes.GridDataList] = grds
                    sumgrd = params[FixProcTypes.MulData][0](mulparams)
                    
                    if sumgrd is None:
                        LogLib.logger.error('FixData check_data_single_pre_mul_obs process sum error %s' % (str(readparams)))
                        if quit_when_error:
                            return
                        else:
                            continue
                    
                except Exception as dtdata:
                    LogLib.logger.error('FixData check_data_single_pre_mul_obs process error %s %s' % (str(fullpaths), str(dtdata)))
                    raise dtdata

            wparams = params[FixProcTypes.WriteData][1]
            wparams[FixParamTypes.GridData] = sumgrd
            wparams[FixParamTypes.DFullPath] = savefullpath

            if params[FixProcTypes.WriteData][0](wparams):
                LogLib.logger.info('FixData check_data_single_pre_mul_obs over %s' % (savefullpath))
            else:
                LogLib.logger.error('FixData check_data_single_pre_mul_obs write file error %s %s' % (str(wparams), savefullpath))
        except Exception as data:
            LogLib.logger.error('FixData check_data_single_pre_mul_obs except %s' % (str(data)))
            
    '''
    #使用fix_data替代
    def fix_data_qinghai(self, params):
        try:
            LogLib.logger.info('FixData fix_data_qinghai start')
            dt_list = params[FixProcTypes.DTList][0](params[FixProcTypes.DTList][1])
            LogLib.logger.debug('FixData fix_data_qinghai dt_list:%s' % str(dt_list))

            for dt in dt_list:
                try:
                    LogLib.logger.info('FixData fix_data_qinghai process datetime start %s' % (dt.strftime('%Y-%m-%d %H:%M:%S')))

                    flistparams = params[FixProcTypes.FileList][1]
                    flistparams[FixParamTypes.DT] = dt

                    fixfullpaths = params[FixProcTypes.FileList][0](flistparams)
                    if fixfullpaths == None or len(fixfullpaths) == 0:
                        LogLib.logger.info('FixData fix_data_qinghai process datetime no file %s' % (dt.strftime('%Y-%m-%d %H:%M:%S')))
                        continue

                    LogLib.logger.debug('FixData fix_data_qinghai process fixfullpaths %s:%s' % (dt.strftime('%Y-%m-%d %H:%M:%S'), str(fixfullpaths)))
                    dt_data = dt
                    if FixParamTypes.TZ_Delta in params[FixProcTypes.WriteData][1]:
                        dt_data = dt + datetime.timedelta(hours=params[FixProcTypes.WriteData][1][FixParamTypes.TZ_Delta])

                    for (fixfullpath, savefullpathinfo) in fixfullpaths.items():
                        savefullpath = savefullpathinfo[0]
                        seqnum = savefullpathinfo[1]

                        LogLib.logger.info('FixData fix_data_qinghai process file start %s %s' % (fixfullpath, savefullpath))

                        readparams = params[FixProcTypes.ReadData][1]
                        readparams[FixParamTypes.SFullPath] = fixfullpath
                        grd = params[FixProcTypes.ReadData][0](readparams)
                        if grd is None:
                            LogLib.logger.warning('FixData fix_data_qinghai read file warn %s %s' % (fixfullpath, savefullpath))
                            #return
                            continue
                        
                        for procobj in params[FixProcTypes.ModifyData]:
                            mparams = procobj[1]
                            mparams[FixParamTypes.GridData] = grd

                            grd = procobj[0](mparams)
                            if grd is None:
                                LogLib.logger.error('FixData fix_data_qinghai modify file error %s %s' % (fixfullpath, str(procobj)))
                                return
                            
                        wparams = params[FixProcTypes.WriteData][1]
                        wparams[FixParamTypes.GridData] = grd
                        wparams[FixParamTypes.DFullPath] = savefullpath
                        wparams[FixParamTypes.DT] = dt_data
                        wparams[FixParamTypes.SeqNum] = seqnum

                        if params[FixProcTypes.WriteData][0](wparams):
                            LogLib.logger.info('FixData fix_data_qinghai process file over %s %s' % (fixfullpath, savefullpath))
                        else:
                            LogLib.logger.error('FixData fix_data_qinghai write file error %s %s' % (fixfullpath, savefullpath))
                            return

                    LogLib.logger.info('FixData fix_data_qinghai process datetime over %s' % (dt.strftime('%Y-%m-%d %H:%M:%S')))
                except Exception as dtdata:
                    LogLib.logger.error('FixData fix_data_qinghai process error %s %s' % (dt.strftime('%Y-%m-%d %H:%M:%S'), str(dtdata)))
                    raise dtdata

            LogLib.logger.info('FixData fix_data_qinghai over')
        except Exception as data:
            LogLib.logger.error('FixData fix_data_qinghai except %s' % (str(data)))
            '''
    '''
    #使用fix_data替代
    #处理彩虹多时效的文本数据
    def fix_data_caihong_seq(self, params):
        try:
            LogLib.logger.info('FixData fix_data_caihong_seq start')
            dt_list = params[FixProcTypes.DTList][0](params[FixProcTypes.DTList][1])
            LogLib.logger.debug('FixData fix_data_caihong_seq dt_list:%s' % str(dt_list))

            for dt in dt_list:
                try:
                    LogLib.logger.info('FixData fix_data_caihong_seq process datetime start %s' % (dt.strftime('%Y-%m-%d %H:%M:%S')))

                    flistparams = params[FixProcTypes.FileList][1]
                    flistparams[FixParamTypes.DT] = dt

                    fixfullpaths = params[FixProcTypes.FileList][0](flistparams)
                    if fixfullpaths == None or len(fixfullpaths) == 0:
                        LogLib.logger.info('FixData fix_data_caihong_seq process datetime no file %s' % (dt.strftime('%Y-%m-%d %H:%M:%S')))
                        continue

                    LogLib.logger.debug('FixData fix_data_caihong_seq process fixfullpaths %s:%s' % (dt.strftime('%Y-%m-%d %H:%M:%S'), str(fixfullpaths)))
                    
                    for (fixfullpath, savefullpathinfo) in fixfullpaths.items():
                        savefullpath = savefullpathinfo[0]
                        seqnum = savefullpathinfo[1]
                        dtsave = savefullpathinfo[2]

                        LogLib.logger.info('FixData fix_data_caihong_seq process file start %s %s' % (fixfullpath, savefullpath))

                        readparams = params[FixProcTypes.ReadData][1]
                        readparams[FixParamTypes.SFullPath] = fixfullpath
                        readparams[FixParamTypes.DT] = dtsave

                        grd = params[FixProcTypes.ReadData][0](readparams)
                        if grd is None:
                            LogLib.logger.warning('FixData fix_data_caihong_seq read file warn %s %s' % (fixfullpath, savefullpath))
                            #return
                            continue
                        
                        for procobj in params[FixProcTypes.ModifyData]:
                            mparams = procobj[1]
                            mparams[FixParamTypes.GridData] = grd

                            grd = procobj[0](mparams)
                            if grd is None:
                                LogLib.logger.error('FixData fix_data_caihong_seq modify file error %s %s' % (fixfullpath, str(procobj)))
                                return
                            
                        wparams = params[FixProcTypes.WriteData][1]
                        wparams[FixParamTypes.GridData] = grd
                        wparams[FixParamTypes.DFullPath] = savefullpath

                        if params[FixProcTypes.WriteData][0](wparams):
                            LogLib.logger.info('FixData fix_data_caihong_seq process file over %s %s' % (fixfullpath, savefullpath))
                        else:
                            LogLib.logger.error('FixData fix_data_caihong_seq write file error %s %s' % (fixfullpath, savefullpath))
                            return

                    LogLib.logger.info('FixData fix_data_caihong_seq process datetime over %s' % (dt.strftime('%Y-%m-%d %H:%M:%S')))
                except Exception as dtdata:
                    LogLib.logger.error('FixData fix_data_caihong_seq process error %s %s' % (dt.strftime('%Y-%m-%d %H:%M:%S'), str(dtdata)))
                    raise dtdata

            LogLib.logger.info('FixData fix_data_caihong_seq over')
        except Exception as data:
            LogLib.logger.error('FixData fix_data_caihong_seq except %s' % (str(data)))
            '''
            
    def verify_data_tmp_max_and_min(self, params, quit_when_error=False):
        try:
            LogLib.logger.info('FixData verify_data_tmp_max_and_min start')
            dt_list = params[FixProcTypes.DTList][0](params[FixProcTypes.DTList][1])
            LogLib.logger.debug('FixData verify_data_tmp_max_and_min dt_list:%s' % str(dt_list))

            for dt in dt_list:
                try:
                    LogLib.logger.info('FixData verify_data_tmp_max_and_min process datetime start %s' % (dt.strftime('%Y-%m-%d %H:%M:%S')))

                    flistparams = params[FixProcTypes.FileList][1]
                    flistparams[FixParamTypes.DT] = dt

                    savefullpath, fixfullpaths = params[FixProcTypes.FileList][0](flistparams)
                    if savefullpath is None or fixfullpaths is None:
                        if quit_when_error:
                            return
                        else:
                            continue

                    if savefullpath == '' or len(fixfullpaths) == 0:
                        LogLib.logger.info('FixData verify_data_tmp_max_and_min process datetime no file %s' % (dt.strftime('%Y-%m-%d %H:%M:%S')))
                        continue

                    LogLib.logger.debug('FixData verify_data_tmp_max_and_min process fixfullpaths %s:%s' % (dt.strftime('%Y-%m-%d %H:%M:%S'), str(fixfullpaths)))

                    grdlist = []
                    LogLib.logger.info('FixData verify_data_tmp_max_and_min process file start %s' % (fixfullpaths))

                    readparams = params[FixProcTypes.ReadData][1]
                    readparams[FixParamTypes.SFullPaths] = fixfullpaths

                    grdlist = params[FixProcTypes.ReadData][0](readparams)
                    if grdlist is None:
                        LogLib.logger.error('FixData verify_data_tmp_max_and_min read file error %s' % (fixfullpath))
                        if quit_when_error:
                            return
                        else:
                            continue

                    sumgrd = None

                    mulparams = params[FixProcTypes.MulData][1]
                    #mulparams[FixParamTypes.DstGridData] = sumgrd
                    mulparams[FixParamTypes.GridDataList] = grdlist
                    sumgrd = params[FixProcTypes.MulData][0](mulparams)
                    
                    if sumgrd is None:
                        LogLib.logger.error('FixData verify_data_tmp_max_and_min process sum error %s' % (dt.strftime('%Y-%m-%d %H:%M:%S')))
                        if quit_when_error:
                            return
                        else:
                            continue
                    
                    wparams = params[FixProcTypes.WriteData][1]
                    wparams[FixParamTypes.GridData] = sumgrd
                    wparams[FixParamTypes.DFullPath] = savefullpath

                    if params[FixProcTypes.WriteData][0](wparams):
                        LogLib.logger.info('FixData verify_data_tmp_max_and_min process file over %s %s' % (dt.strftime('%Y-%m-%d %H:%M:%S'), savefullpath))
                    else:
                        LogLib.logger.error('FixData verify_data_tmp_max_and_min write file error %s %s' % (dt.strftime('%Y-%m-%d %H:%M:%S'), savefullpath))
                        if quit_when_error:
                            return
                        else:
                            continue
                            
                except Exception as dtdata:
                    LogLib.logger.error('FixData verify_data_tmp_max_and_min process error %s %s' % (dt.strftime('%Y-%m-%d %H:%M:%S'), str(dtdata)))
                    raise dtdata

            LogLib.logger.info('FixData verify_data_tmp_max_and_min over')
        except Exception as data:
            LogLib.logger.error('FixData verify_data_tmp_max_and_min except %s' % (str(data)))
            
    #针对单文件根据seq和（或）pnum进行拆分的情况
    def fix_data_muldst(self, params, quit_when_error=False):
        try:
            LogLib.logger.info('FixData fix_data_muldst start')
            dt_list = params[FixProcTypes.DTList][0](params[FixProcTypes.DTList][1])
            LogLib.logger.debug('FixData fix_data_muldst dt_list:%s' % str(dt_list))

            for dt in dt_list:
                try:
                    LogLib.logger.info('FixData fix_data_muldst process datetime start %s' % (dt.strftime('%Y-%m-%d %H:%M:%S')))

                    flistparams = params[FixProcTypes.FileList][1]
                    flistparams[FixParamTypes.DT] = dt

                    savefullpaths, fixfullpath, sdt = params[FixProcTypes.FileList][0](flistparams)
                    if fixfullpath is None or savefullpaths is None:
                        if quit_when_error:
                            return
                        else:
                            continue

                    if fixfullpath == '' or len(savefullpaths) == 0:
                        LogLib.logger.info('FixData fix_data_muldst process datetime no file %s' % (dt.strftime('%Y-%m-%d %H:%M:%S')))
                        continue

                    #LogLib.logger.debug('FixData fix_data_muldst process fixfullpaths %s:%s' % (dt.strftime('%Y-%m-%d %H:%M:%S'), str(fixfullpath)))

                    grdlist = []
                    LogLib.logger.info('FixData fix_data_muldst process file start %s:%s' % (dt.strftime('%Y-%m-%d %H:%M:%S'), fixfullpath))

                    readparams = params[FixProcTypes.ReadData][1]
                    readparams[FixParamTypes.SFullPath] = fixfullpath
                    readparams[FixParamTypes.SeqAndPNum] = list(savefullpaths.keys())

                    grdlist = params[FixProcTypes.ReadData][0](readparams)
                    if grdlist is None:
                        LogLib.logger.error('FixData fix_data_muldst read file error %s:%s' % (dt.strftime('%Y-%m-%d %H:%M:%S'), fixfullpath))
                        if quit_when_error:
                            return
                        else:
                            continue

                    if len(grdlist) == 0:
                        continue

                    wparams = params[FixProcTypes.WriteData][1]
                    wparams[FixParamTypes.GridDataList] = grdlist
                    wparams[FixParamTypes.DFullPaths] = savefullpaths
                    wparams[FixParamTypes.DT] = sdt

                    if params[FixProcTypes.WriteData][0](wparams):
                        LogLib.logger.info('FixData fix_data_muldst process file over %s %s' % (dt.strftime('%Y-%m-%d %H:%M:%S'), str(savefullpaths)))
                    else:
                        LogLib.logger.error('FixData fix_data_muldst write file error %s %s' % (dt.strftime('%Y-%m-%d %H:%M:%S'), str(savefullpaths)))
                        if quit_when_error:
                            return
                        else:
                            continue
                            
                except Exception as dtdata:
                    LogLib.logger.error('FixData fix_data_muldst process error %s %s' % (dt.strftime('%Y-%m-%d %H:%M:%S'), str(dtdata)))
                    raise dtdata

            LogLib.logger.info('FixData fix_data_muldst over')
        except Exception as data:
            LogLib.logger.error('FixData fix_data_muldst except %s' % (str(data)))
            
    def fix_data_mulsrc_muldst(self, params, quit_when_error=False):
        try:
            LogLib.logger.info('FixData fix_data_mulsrc_muldst start')
            dt_list = params[FixProcTypes.DTList][0](params[FixProcTypes.DTList][1])
            LogLib.logger.debug('FixData fix_data_mulsrc_muldst dt_list:%s' % str(dt_list))

            for dt in dt_list:
                try:
                    LogLib.logger.info('FixData fix_data_mulsrc_muldst process datetime start %s' % (dt.strftime('%Y-%m-%d %H:%M:%S')))

                    flistparams = params[FixProcTypes.FileList][1]
                    flistparams[FixParamTypes.DT] = dt

                    savefullpaths, fixfullpaths, sdt = params[FixProcTypes.FileList][0](flistparams)
                    if fixfullpaths is None or savefullpaths is None:
                        if quit_when_error:
                            return
                        else:
                            continue

                    if len(fixfullpaths) == 0 or len(savefullpaths) == 0:
                        LogLib.logger.info('FixData fix_data_mulsrc_muldst process datetime no file %s' % (dt.strftime('%Y-%m-%d %H:%M:%S')))
                        continue

                    #LogLib.logger.debug('FixData fix_data_mulsrc_muldst process fixfullpaths %s:%s' % (dt.strftime('%Y-%m-%d %H:%M:%S'), str(fixfullpaths)))

                    grdlist = []
                    LogLib.logger.info('FixData fix_data_mulsrc_muldst process file start %s:%s' % (dt.strftime('%Y-%m-%d %H:%M:%S'), fixfullpaths))

                    readparams = params[FixProcTypes.ReadData][1]
                    readparams[FixParamTypes.SFullPaths] = fixfullpaths
                    readparams[FixParamTypes.SeqAndPNum] = list(savefullpaths.keys())

                    grdlist = params[FixProcTypes.ReadData][0](readparams)
                    if grdlist is None:
                        LogLib.logger.error('FixData fix_data_mulsrc_muldst read file error %s:%s' % (dt.strftime('%Y-%m-%d %H:%M:%S'), fixfullpaths))
                        if quit_when_error:
                            return
                        else:
                            continue

                    if len(grdlist) == 0:
                        continue

                    wparams = params[FixProcTypes.WriteData][1]
                    wparams[FixParamTypes.GridDataList] = grdlist
                    wparams[FixParamTypes.DFullPaths] = savefullpaths
                    wparams[FixParamTypes.DT] = sdt

                    if params[FixProcTypes.WriteData][0](wparams):
                        LogLib.logger.info('FixData fix_data_mulsrc_muldst process file over %s %s' % (dt.strftime('%Y-%m-%d %H:%M:%S'), str(savefullpaths)))
                    else:
                        LogLib.logger.error('FixData fix_data_mulsrc_muldst write file error %s %s' % (dt.strftime('%Y-%m-%d %H:%M:%S'), str(savefullpaths)))
                        if quit_when_error:
                            return
                        else:
                            continue
                            
                except Exception as dtdata:
                    LogLib.logger.error('FixData fix_data_mulsrc_muldst process error %s %s' % (dt.strftime('%Y-%m-%d %H:%M:%S'), str(dtdata)))
                    raise dtdata

            LogLib.logger.info('FixData fix_data_mulsrc_muldst over')
        except Exception as data:
            LogLib.logger.error('FixData fix_data_mulsrc_muldst except %s' % (str(data)))
            
	#一次确定出所有时间点需要的源文件和目标文件全路径
    #当前用于app数据源融合
    def fix_data_muldst_notime(self, params, quit_when_error=False):
        try:
            LogLib.logger.info('FixData fix_data_muldst_notime start')
            dt_list = []
            if FixProcTypes.DTList in params:
                dt_list = params[FixProcTypes.DTList][0](params[FixProcTypes.DTList][1])
            LogLib.logger.debug('FixData fix_data_muldst_notime dt_list:%s' % str(dt_list))

            flistparams = params[FixProcTypes.FileList][1]
            flistparams[FixParamTypes.DTS] = dt_list

            savefullpaths, fixfullpath, sdt = params[FixProcTypes.FileList][0](flistparams)
            if fixfullpath == None:
                LogLib.logger.warning('FixData fix_data_muldst_notime process datetime no file %s' % (str(flistparams)))
                return
            
            if savefullpaths is None or len(savefullpaths) == 0:
                LogLib.logger.warning('FixData fix_data_muldst_notime process datetime not need process %s' % (str(flistparams)))
                return

            LogLib.logger.debug('FixData fix_data_muldst_notime process fixfullpath %s' % (fixfullpath))

            readparams = params[FixProcTypes.ReadData][1]
            readparams[FixParamTypes.SFullPath] = fixfullpath
            readparams[FixParamTypes.SeqAndPNum] = list(savefullpaths.keys())

            grdlist = params[FixProcTypes.ReadData][0](readparams)
            if grdlist is None:
                LogLib.logger.error('FixData fix_data_muldst_notime read file error %s %s' % (fixfullpath, str(savefullpaths)))
                return

            wparams = params[FixProcTypes.WriteData][1]
            wparams[FixParamTypes.GridDataList] = grdlist
            wparams[FixParamTypes.DFullPaths] = savefullpaths
            wparams[FixParamTypes.DT] = sdt

            if params[FixProcTypes.WriteData][0](wparams):
                LogLib.logger.info('FixData fix_data_muldst_notime process file over %s %s' % (fixfullpath, str(savefullpaths)))
            else:
                LogLib.logger.error('FixData fix_data_muldst_notime write file error %s %s' % (fixfullpath, str(savefullpaths)))
                    
            LogLib.logger.info('FixData fix_data_muldst_notime over')
        except Exception as data:
            LogLib.logger.error('FixData fix_data_muldst_notime except %s' % (str(data)))
            
if __name__ == '__main__':
    print('done')
