#!/usr/bin/python
# -*- coding: utf-8 -*-
#Filename: fixfileTypes.py

'''
Created on Mar 22, 2021

@author: anduin
'''

from enum import Enum

class FixFileTypes(Enum):
    #qpe需要处理文件的时间，时效
    DT_QPE_1hr = 'DT_QPE_1hr'
    #qpe需要处理文件的修改时间
    MDT_QPE_1hr = 'MDT_QPE_1hr'
    #qpe需要提前处理的文件的时间，时效
    DT_QPE_1hr_N = 'DT_QPE_1hr_N'
    #qpe需要提前处理的文件的修改时间
    MDT_QPE_1hr_N = 'MDT_QPE_1hr_N'

    #滚动预报
    DT_RP_02401 = 'DT_RP_02401'
    #国家指导报
    DT_SCMOC_24001 = 'DT_SCMOC_24001'
    #国省融合
    DT_SMERGE_24003 = 'DT_SMERGE_24003'
    #国省融合与国家指导报插值逐小时
    DT_SMERGE_03601 = 'DT_SMERGE_03601'

    #要素
    DT_TMP= 'DT_TMP'

    #站点id
    StaID = 'id'
    #纬度
    Lat = 'lat'
    #经度
    Lon = 'lon'
    #海拔
    Alt = 'alt'

    #风速
    WIND_S = 'wind_s'
    #风向
    WIND_D = 'wind_d'

    #2米气温
    TT2 = 'TT2'
    #1小时降水
    RR1 = 'RR1'
    #3小时降水
    RR3 = 'RR3'
    #24小时降水
    R24 = 'R24'
    #2分钟风向
    WDS = 'WDS'
    #2分钟风速
    UVS = 'UVS' 
    #总云
    TCC = 'TCC'
    #高云状
    CFH = 'CFH' 
    #低云状
    CFL = 'CFL'
    #中云状
    CFM = 'CFM'
    #2米相对湿度
    RH2 = 'RH2'
    #地面气压
    PPS = 'PPS'
    #2米露点温度
    DPT = 'DPT'
    #能见度
    VIS = 'VIS'

if __name__ == '__main__':
    a=FixFileTypes.DT_QPE_1hr
    print(a.value)
    print(FixFileTypes.DT_QPE_1hr)
    
    print('test done')