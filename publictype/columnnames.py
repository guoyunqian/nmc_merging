#!/usr/bin/python
# -*- coding: utf-8 -*-
#Filename: columnnames.py

'''
Created on Apr 4, 2021

@author: anduin
'''

from enum import Enum

class ColumnNames(Enum):
    #结果名称
    Result = 'result'
    #meteva站点数据默认数据列名
    MebStaDefault = 'data0'

    #省名称的列名
    Area = 'area'
    #站点id
    StaID = 'id'
    #经度
    Lon = 'lon'
    #纬度
    Lat = 'lat'
    #海拔
    Alt = 'alt'

    #时效'forecast_time'
    Seq = 'seq'
    #温度
    Tem = 'tem'
    TEM = 'TEM'
    #相对湿度'relative_humidity'
    RH = 'rh'
    #风向
    Wind_D = 'win_d'
    #风速
    Wind_S = 'win_s'
    #气压'air_pressure'
    AP = 'ap'
    #降水量'precipitation'
    Pre = 'pre'
    #总云量'total_cloud'
    TC = 'tc'
    #低云量'low_cloud'
    LC = 'lc'
    #天气现象'weather_phenomena'
    WP = 'wp'
    #能见度'visibility'
    VIS = 'vis'
    #最高温度'tem_max'
    TMX = 'tmx'
    #最低温度'tem_min'
    TMI = 'tmi'
    #最大相对湿度'relative_humidity_max'
    RHMX = 'rhmx'
    #最小相对湿度'relative_humidity_min'
    RHMI = 'rhmi'
    #24小时降水量'total_precipitation_24h'
    TP24H = 'tp24'
    #12小时降水量'total_precipitation_12h'
    TP12H = 'tp12'
    #12小时总云量'total_cloud_12h'
    TC12H = 'tc12'
    #12小时低云量'low_cloud_12h'
    LC12H = 'lc12'
    #12小时天气现象'weather_phenomena_12h'
    WP12H = 'wp12'
    #12小时风向
    Wind_D_12H = 'win_d_12h'
    #12小时风速
    Wind_S_12H = 'win_s_12h'

if __name__ == '__main__':
    a=ColumnNames.Area
    print(a.value)
    print(ColumnNames.Area)
    
    print('test done')