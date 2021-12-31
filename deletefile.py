#!/usr/bin/python
# -*- coding: utf-8 -*-
#Filename: deletefile.py

"""
Created on Nov 4, 2020

@author: anduin
"""

import os
import datetime
import shutil
import re

def deletefiles(filepath, curdate, days=7, dir_fmt=r'%Y%m%d'):
    deldate = curdate - datetime.timedelta(days=days)

    for fn in os.listdir(filepath):
        fullpath = os.path.join(filepath, fn)
        if os.path.isdir(fullpath):
            dt = datetime.datetime.strptime(fn, dir_fmt)
            if dt <= deldate:
                shutil.rmtree(fullpath)

def deltree():
    curdate = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    #地面1小时降水实况
    #fix_dict = r'/space/cmadaas/dpl/NWFD01/data/Observation/SURFACE/Precipitation/SUR_01hr_h5'
    delta_t = 10   #天
    dir_fmt = r'%Y%m%d'

    #deletefiles(fix_dict, curdate, days=delta_t, dir_fmt=dir_fmt)
    
    #地面24小时降水实况
    #fix_dict = r'/space/cmadaas/dpl/NWFD01/data/Observation/SURFACE/Precipitation/SUR_24hr_h5'

    #deletefiles(fix_dict, curdate, days=delta_t, dir_fmt=dir_fmt)

    #地面1分钟降水实况
    #fix_dict = r'/space/cmadaas/dpl/NWFD01/data/Observation/SURFACE/Precipitation/SUR_01min_h5'

    #deletefiles(fix_dict, curdate, days=delta_t, dir_fmt=dir_fmt)

    #降水分析10分钟
    fix_dict = r'/space/cmadaas/dpl/NWFD01/data/Observation/CLDAS/Precipitation/Rain_10min_5km'

    deletefiles(fix_dict, curdate, days=delta_t, dir_fmt=dir_fmt)

    #降水分析二源
    fix_dict = r'/space/cmadaas/dpl/NWFD01/data/Observation/CLDAS/Precipitation/Rain2S_01Hr_5km'

    deletefiles(fix_dict, curdate, days=delta_t, dir_fmt=dir_fmt)
    
    #降水分析三源
    fix_dict = r'/space/cmadaas/dpl/NWFD01/data/Observation/CLDAS/Precipitation/Rain3S_01Hr_5km'

    deletefiles(fix_dict, curdate, days=delta_t, dir_fmt=dir_fmt)
    
def delfile(filepath, curdate, file_fmt):
    fmt = curdate.strftime(file_fmt)
    for fn in os.listdir(filepath):
        fullpath = os.path.join(filepath, fn)
        if os.path.isfile(fullpath):
            rsts =  re.findall(fmt, fn)
            if len(rsts) > 0:
                os.remove(fullpath)

def delfiles():
    curdt = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    delta_t = 10   #天
    file_fmt = r'^%Y%m%d([0-9]{2}\.[0-9]{3})'

    curdt -= datetime.timedelta(days=delta_t)

    for i in range(2):
        curdate = curdt - datetime.timedelta(days=i)

        delfile(r'/space/cmadaas/dpl/NWFD01/data/mulblend', curdate, file_fmt)
        
        delfile(r'/space/cmadaas/dpl/NWFD01/data/mulblend_eda10', curdate, file_fmt)
        
        delfile(r'/space/cmadaas/dpl/NWFD01/data/mulblend_pph', curdate, file_fmt)
        
        delfile(r'/space/cmadaas/dpl/NWFD01/data/mulblend_pre', curdate, file_fmt)
        
        delfile(r'/space/cmadaas/dpl/NWFD01/data/mulblend_rh', curdate, file_fmt)
        
        delfile(r'/space/cmadaas/dpl/NWFD01/data/mulblend_tmax', curdate, file_fmt)
        
        delfile(r'/space/cmadaas/dpl/NWFD01/data/mulblend_tmin', curdate, file_fmt)
        
def mvdir(srcdir, dstdir, curdate, dir_fmt):
    fmt = curdate.strftime(dir_fmt)
    for fn in os.listdir(srcdir):
        fullpath = os.path.join(srcdir, fn)
        if os.path.isdir(fullpath):
            rsts =  re.findall(fmt, fn)
            if len(rsts) > 0:
                shutil.move(fullpath, os.path.join(dstdir, fn))

def mvdirs():
    curdt = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    delta_t = 10   #天
    dir_fmt = r'%Y%m%d'

    curdt -= datetime.timedelta(days=delta_t)

    for i in range(2):
        curdate = curdt - datetime.timedelta(days=i)
        srcdir = curdate.strftime(r'/space/cmadaas/dpl/NWFD01/data/mulblend_grib2/BABJ/%Y')
        dstdir = curdate.strftime(r'/space/cmadaas/dpl/NWFD01/Mulblend/mulblend_grib2/BABJ/%Y')

        if not os.path.exists(dstdir):
            os.makedirs(dstdir)

        mvdir(srcdir, dstdir, curdate, dir_fmt)
        
def mvfile(srcdir, dstdir, curdate, file_fmt):
    fmt = curdate.strftime(file_fmt)
    for fn in os.listdir(srcdir):
        fullpath = os.path.join(srcdir, fn)
        if os.path.isfile(fullpath):
            rsts =  re.findall(fmt, fn)
            if len(rsts) > 0:
                shutil.move(fullpath, os.path.join(dstdir, fn))

def mvfiles():
    curdt = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    delta_t = 10   #天
    #Z_SEVP_C_BABJ_20211223173740_P_RFFC-SNWFD-2021122320-24003.h5
    file_fmt = r'Z_SEVP_C_BABJ_([0-9]{14})_P_RFFC-SNWFD-%Y%m%d([0-9]{2})-([0-9]{5}).h5'

    curdt -= datetime.timedelta(days=delta_t)

    for i in range(2):
        curdate = curdt - datetime.timedelta(days=i)
        srcdir = r'/space/cmadaas/dpl/NWFD01/data/mulblend_hdf'
        dstdir = curdate.strftime(r'/space/cmadaas/dpl/NWFD01/Mulblend/mulblend_hdf/%Y')

        if not os.path.exists(dstdir):
            os.makedirs(dstdir)

        mvfile(srcdir, dstdir, curdate, file_fmt)
        
        
if __name__ == '__main__':
    delfiles()

    mvdirs()

    mvfiles()

    print('done')
