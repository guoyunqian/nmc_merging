#!/usr/bin/python
# -*- coding: utf-8 -*-
#Filename: fixwritedata.py

'''
Created on Aug 21, 2020

@author: anduin
'''

import os
import numpy as np
import shutil

from logmodule.loglib import *
from publictype.fixparamtypes import FixParamTypes

class FixWriteData(object):
    def path_exists(self, path, creat_dir=True):
        if not os.path.exists(path):
            if creat_dir:
                os.makedirs(path)
            else:
                raise Exception('path not exist')

    #保存站点数据为m3格式
    def save_stddata_to_m3_no_meb(self, params):
        savegrd = params[FixParamTypes.GridData]
        save_path = params[FixParamTypes.DFullPath]
        dt = params[FixParamTypes.DT]
        level = params[FixParamTypes.Level] if FixParamTypes.Level in params else 0
        creat_dir = params[FixParamTypes.IsCreatDir] if FixParamTypes.IsCreatDir in params else True
        effectiveNum = params[FixParamTypes.Decimals] if FixParamTypes.Decimals in params else 4
        scaled_decimals = params[FixParamTypes.ScaleDecimals] if FixParamTypes.ScaleDecimals in params else 4
        title = params[FixParamTypes.Title] if FixParamTypes.Title in params else None

        save_path_tmp = save_path + '.tmp'

        try:
            LogLib.logger.info('FixWriteData save_stddata_to_m3_no_meb start {}'.format(save_path))
            
            path,file = os.path.split(save_path)
            self.path_exists(path, creat_dir)
            
            if title is None:
                end = len(save_path)
                start = max(0, end - 16)
                title = save_path[start:end]

            title = ("diamond 3 "+ title +"\n" + dt.strftime('%Y %m %d %H') + " " + str(int(level)) + ' 0 0 0 0 1 ' + str(len(savegrd)))

            # 二维数组写入micaps文件
            #format_str = "%." + str(effectiveNum) + "f "
            format_str = "%-8d %8.{0}f %8.{1}f %8.{2}f %8.{3}f".format(scaled_decimals, scaled_decimals, scaled_decimals, effectiveNum)
            np.savetxt(save_path_tmp, savegrd, delimiter=' ', fmt=format_str, header=title, comments='')


            shutil.move(save_path_tmp, save_path)

            LogLib.logger.info('FixWriteData save_stddata_to_m3_no_meb over {}'.format(save_path))

            return True
        except Exception as data:
            LogLib.logger.error('FixWriteData save_stddata_to_m3_no_meb except {} {}'.format(params, data))
            
            if os.path.exists(save_path_tmp):
                os.remove(save_path_tmp)

            raise data
        
    def proc_sign(self, d, s, e):
        if s < e:
            if d > 0:
                return d
            else:
                return -d
        else:
            if d > 0:
                return -d
            else:
                return d

    def compute_m4_inte(self, vmax, vmin):
        import math
        
        vmax = math.ceil(vmax)
        vmin = math.ceil(vmin)
            
        dif = (vmax - vmin) / 10.0
        inte = 1
        if dif != 0:
            inte = math.pow(10, math.floor(math.log10(dif)))
        # 用基本间隔，将最大最小值除于间隔后小数点部分去除，最后把间隔也整数化
        r = dif / inte
        if r < 3 and r >= 1.5:
            inte = inte * 2
        elif r < 4.5 and r >= 3:
            inte = inte * 4
        elif r < 5.5 and r >= 4.5:
            inte = inte * 5
        elif r < 7 and r >= 5.5:
            inte = inte * 6
        elif r >= 7:
            inte = inte * 8
        vmin = inte * ((int)(vmin / inte) - 1)
        vmax = inte * ((int)(vmax / inte) + 1)

        return (vmax, vmin, inte)

    #savegrd是二维数据
    def save_griddata_to_m4_no_meb(self, params):
        savegrd = params[FixParamTypes.GridData]
        save_path = params[FixParamTypes.DFullPath]
        dt = params[FixParamTypes.DT]
        seqnum = params[FixParamTypes.SeqNum] if (FixParamTypes.SeqNum in params and params[FixParamTypes.SeqNum] is not None) else 0
        level = params[FixParamTypes.Level] if FixParamTypes.Level in params else 0
        creat_dir = params[FixParamTypes.IsCreatDir] if FixParamTypes.IsCreatDir in params else True
        effectiveNum = params[FixParamTypes.Decimals] if FixParamTypes.Decimals in params else 6
        scaled_decimals = params[FixParamTypes.ScaleDecimals] if FixParamTypes.ScaleDecimals in params else 4
        title = params[FixParamTypes.Title] if FixParamTypes.Title in params else None

        nlon = params[FixParamTypes.NLon]
        nlat = params[FixParamTypes.NLat]
        slon = params[FixParamTypes.SLon]
        slat = params[FixParamTypes.SLat]
        elon = params[FixParamTypes.ELon]
        elat = params[FixParamTypes.ELat]
        dlon = params[FixParamTypes.DLon]
        dlat = params[FixParamTypes.DLat]

        dlon = self.proc_sign(dlon, slon, elon)
        dlat = self.proc_sign(dlat, slat, elat)

        save_path_tmp = save_path + '.tmp'

        try:
            LogLib.logger.info('FixWriteData save_griddata_to_m4_no_meb start %s' % (save_path))

            path,file = os.path.split(save_path)
            self.path_exists(path, creat_dir)
            
            vmax = max(savegrd.flatten())
            vmin = min(savegrd.flatten())

            vmax, vmin, inte = self.compute_m4_inte(vmax, vmin)

            if title is None:
                end = len(save_path)
                start = max(0, end - 16)
                title = save_path[start:end]

            scaled_decimals_fmt = "{:.%df}" % scaled_decimals
            title = ("diamond 4 "+ title +"\n"
                        + dt.strftime('%Y %m %d %H') + " " + str(int(seqnum)) + " " + str(int(level)) + " "
                        + scaled_decimals_fmt.format(dlon) + " " + scaled_decimals_fmt.format(dlat) + " "
                        + scaled_decimals_fmt.format(slon) + " " + scaled_decimals_fmt.format(elon) + " "
                        + scaled_decimals_fmt.format(slat) + " " + scaled_decimals_fmt.format(elat) + " "
                        + str(int(nlon)) + " " + str(int(nlat)) + " "
                        + str(inte) + " " + str(vmin) + " " + str(vmax) + " 1 0")

            # 二维数组写入micaps文件
            format_str = "%." + str(effectiveNum) + "f "

            np.savetxt(save_path_tmp, savegrd, delimiter=' ', fmt=format_str, header=title, comments='')

            shutil.move(save_path_tmp, save_path)

            LogLib.logger.info('FixWriteData save_griddata_to_m4_no_meb over %s' % (save_path))

            return True
        except Exception as data:
            LogLib.logger.error('FixWriteData save_griddata_to_m4_no_meb except:%s' % (str(data)))
            
            if os.path.exists(save_path_tmp):
                os.remove(save_path_tmp)

            raise data
        
    #savegrd数据为pygrib读出的grib文件中的单个grib结构
    def save_grib_to_m4(self, params):
        savegrd = params[FixParamTypes.GridData]
        save_path = params[FixParamTypes.DFullPath]
        dt = params[FixParamTypes.DT]
        seq = params[FixParamTypes.SeqNum] if (FixParamTypes.SeqNum in params and params[FixParamTypes.SeqNum] is not None) else 0
        level = params[FixParamTypes.Level] if FixParamTypes.Level in params else 0
        creat_dir = params[FixParamTypes.IsCreatDir] if FixParamTypes.IsCreatDir in params else True
        effectiveNum = params[FixParamTypes.Decimals] if FixParamTypes.Decimals in params else 6
        title = params[FixParamTypes.Title] if FixParamTypes.Title in params else None
        
        try:
            LogLib.logger.info('FixWriteData save_grib_to_m4 start %s' % (save_path))

            curparams = {}
            gd = savegrd.values
            if type(gd) is np.ma.core.MaskedArray:
                gd = gd.data

            curparams[FixParamTypes.GridData] = gd
            curparams[FixParamTypes.DFullPath] = save_path
            curparams[FixParamTypes.DT] = dt
            curparams[FixParamTypes.SeqNum]  = seq
            curparams[FixParamTypes.Level]  = level
            curparams[FixParamTypes.IsCreatDir] = creat_dir
            curparams[FixParamTypes.Decimals] = effectiveNum
            curparams[FixParamTypes.Title] = title
            
            curparams[FixParamTypes.NLon] = savegrd.Ni
            curparams[FixParamTypes.NLat] = savegrd.Nj
            curparams[FixParamTypes.SLon] = savegrd.longitudeOfFirstGridPointInDegrees
            curparams[FixParamTypes.SLat] = savegrd.latitudeOfFirstGridPointInDegrees
            curparams[FixParamTypes.ELon] = savegrd.longitudeOfLastGridPointInDegrees
            curparams[FixParamTypes.ELat] = savegrd.latitudeOfLastGridPointInDegrees
            curparams[FixParamTypes.DLon] = savegrd.iDirectionIncrementInDegrees
            curparams[FixParamTypes.DLat] = savegrd.jDirectionIncrementInDegrees

            rst = self.save_griddata_to_m4_no_meb(curparams)

            if rst:
                LogLib.logger.info('FixWriteData save_grib_to_m4 over %s' % (save_path))
            else:
                LogLib.logger.error('FixWriteData save_grib_to_m4 error %s' % (save_path))

            return rst

        except Exception as data:
            LogLib.logger.error('FixWriteData save_grib_to_m4 except:%s' % (str(data)))

            raise data
        
    #savegrds数据为pygrib读出的grib文件中的时效为key的grib结构的字典，save_paths是时效为key的目标文件全路径的字典类型数据
    def save_gribs_to_m4(self, params):
        savegrds = params[FixParamTypes.GridDataList]
        save_paths = params[FixParamTypes.DFullPaths]
        dt = params[FixParamTypes.DT]
        level = params[FixParamTypes.Level] if FixParamTypes.Level in params else 0
        creat_dir = params[FixParamTypes.IsCreatDir] if FixParamTypes.IsCreatDir in params else True
        effectiveNum = params[FixParamTypes.Decimals] if FixParamTypes.Decimals in params else 6
        title = params[FixParamTypes.Title] if FixParamTypes.Title in params else None
        
        try:
            LogLib.logger.info('FixWriteData save_grib_to_m4 start %s' % (str(dt)))

            curparams = {}
            curparams[FixParamTypes.DT] = dt
            curparams[FixParamTypes.Level]  = level
            curparams[FixParamTypes.IsCreatDir] = creat_dir
            curparams[FixParamTypes.Decimals] = effectiveNum
            curparams[FixParamTypes.Title] = title
            
            haveerr = False
            for k, path in save_paths.items():
                if k in savegrds:
                    seq = 0
                    site = k.find('_')
                    if site > 0:
                        seq = int(k[site+1:])
                    else:
                        seq = int(k)

                    curparams[FixParamTypes.GridData] = savegrds[k]
                    curparams[FixParamTypes.SeqNum] = seq
                    curparams[FixParamTypes.DFullPath] = path

                    rst = self.save_grib_to_m4(curparams)
                    if not rst:
                        haveerr = True
                else:
                    LogLib.logger.warning('FixWriteData save_gribs_to_m4 no data:%s %s' % (str(dt), str(k)))
                    #haveerr = True

            if haveerr:
                 LogLib.logger.error('FixWriteData save_grib_to_m4 have error:%s' % (str(dt)))
            else:
                LogLib.logger.info('FixWriteData save_grib_to_m4 over %s' % (str(dt)))

            return not haveerr

        except Exception as data:
            LogLib.logger.error('FixWriteData save_grib_to_m4 except:%s %s' % (str(dt), str(data)))

            raise data
        
if __name__ == '__main__':
    print('done')
