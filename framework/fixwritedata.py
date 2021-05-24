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

from publictype.fixparamtypes import FixParamTypes

class FixWriteData(object):
    def __init__(self, logger):
        self.logger = logger
        
    def path_exists(self, path, creat_dir=True):
        if not os.path.exists(path):
            if creat_dir:
                os.makedirs(path)
            else:
                raise Exception('path not exist')

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
        
        logger = params[FixParamTypes.CurLogger] if FixParamTypes.CurLogger in params else None
        if logger is None:
            logger = self.logger

        save_path_tmp = save_path + '.tmp'

        try:
            logger.info('FixWriteData save_griddata_to_m4_no_meb start %s' % (save_path))

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

            logger.info('FixWriteData save_griddata_to_m4_no_meb over %s' % (save_path))

            return True
        except Exception as data:
            logger.error('FixWriteData save_griddata_to_m4_no_meb except:%s' % (str(data)))
            
            if os.path.exists(save_path_tmp):
                os.remove(save_path_tmp)

            raise data
        
if __name__ == '__main__':
    print('done')
