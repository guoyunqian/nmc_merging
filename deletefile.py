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

from public.checkfilefunc import deletefiles

if __name__ == '__main__':
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
    

    print('done')
