#!/usr/bin/python
# -*- coding: utf-8 -*-
#Filename: fixmodifydata.py

"""
Created on Aug 21, 2020

@author: anduin
"""

import numpy as np
import copy
import xarray
import pandas as pd
import xarray as xr
import datetime

from logmodule.loglib import *
from publictype.fixparamtypes import FixParamTypes
from publictype.conditiontypes import ConditionTypes

class FixModifyData(object):
    #如果数据是xarray，当前只支持单数据，名字为tp。
    def eliminate_grid_nan(self, params):
        gdata = params[FixParamTypes.GridData]
        default = params[FixParamTypes.Default]
        deepcopy = params[FixParamTypes.DeepCopy]

        try:
            LogLib.logger.info('FixModifyData eliminate_grid_nan start')
            grd = gdata
            if type(gdata) is xarray.core.dataset.Dataset:
                if 'tp' not in gdata.data_vars:
                   for dk in gdata.data_vars:
                       if dk != 'fhour':
                           gdata = gdata.rename(name_dict={'nc_var_name':'tp'})
                           break
                       
                grd = gdata.tp

            if deepcopy:
                grd.values = copy.deepcopy(grd.values)

            a = grd.values
            a[np.isnan(a)] = default

            LogLib.logger.info('FixModifyData eliminate_grid_nan over')

            return gdata
        except Exception as data:
            LogLib.logger.error('FixModifyData eliminate_grid_nan except:%s' % (str(data)))

            raise data
            
    def eliminate_grid_missdata(self, params):
        grd = params[FixParamTypes.GridData]
        miss = params[FixParamTypes.Miss]
        default = params[FixParamTypes.Default]
        usearound = params[FixParamTypes.UseAround]
        decimals = params[FixParamTypes.Decimals]
        deepcopy = params[FixParamTypes.DeepCopy]

        try:
            LogLib.logger.info('FixModifyData eliminate_grid_missdata start')
            if deepcopy:
                grd.values = copy.deepcopy(grd.values)

            a = grd.values
            if usearound:
                a[np.around(a, decimals=decimals) == miss] = default
            else:
                a[a==miss] = default

            LogLib.logger.info('FixModifyData eliminate_grid_missdata over')

            return grd
        except Exception as data:
            LogLib.logger.error('FixModifyData eliminate_grid_missdata except:%s' % (str(data)))

            raise data

    def interp_gg_linear(self, params):
        import meteva.base as meb

        grd = params[FixParamTypes.GridData]
        grid = params[FixParamTypes.GridW]
        outer_value = params[FixParamTypes.Default]
        
        try:
            LogLib.logger.info('FixModifyData interp_gg_linear start')
            savegrd = meb.interp_gg_linear(grd, grid, outer_value=outer_value)
            if savegrd is None:
                LogLib.logger.error('FixModifyData interp_gg_linear error %s' % (str(params)))
                return savegrd
            else:
                LogLib.logger.info('FixModifyData interp_gg_linear over')

            return savegrd
        except Exception as data:
            LogLib.logger.error('FixModifyData interp_gg_linear except %s %s' % (str(params), str(data)))

            raise data

    def change_gird_data_dtype(self, params):
        grd = params[FixParamTypes.GridData]
        dname = params[FixParamTypes.DName]
        s_dtype = params[FixParamTypes.S_DType]
        d_dtype = params[FixParamTypes.D_DType]
        keep_attrs = params[FixParamTypes.KeepAttrs] if FixParamTypes.KeepAttrs in params else True

        try:
            LogLib.logger.info('FixModifyData change_gird_data_dtype start')
            oritype = grd[dname].dtype
            if oritype != s_dtype:
                if oritype == d_dtype:
                    LogLib.logger.info('FixModifyData change_gird_data_dtype no change')
                    return grd
                else:
                    raise Exception('dtype error %s' % str(oritype))

            attrs = None
            if keep_attrs:
                attrs = grd[dname].attrs

            grd[dname] = grd[dname].astype(d_dtype)

            if keep_attrs and attrs is not None:
                grd[dname].attrs = attrs

            LogLib.logger.info('FixModifyData change_gird_data_dtype over')

            return grd
        except Exception as data:
            LogLib.logger.error('FixModifyData change_gird_data_dtype except %s %s' % (str(params), str(data)))

            raise data
        
    #cmadaas数据有些是没有用处的垃圾数据，需要删掉，不然可能无法转成meteva的数据
    def cmadaas_data_del_condition(self, params):
        pddata = params[FixParamTypes.GridData]
        columns = params[FixParamTypes.Columns]
        values = params[FixParamTypes.Values]
        conditions = params[FixParamTypes.Conditions]

        try:
            LogLib.logger.info('FixModifyData cmadaas_data_del_condition start')
            if pddata.empty:
                LogLib.logger.info('FixModifyData cmadaas_data_del_condition over, data empty, no change')
                return pddata

            if len(columns) != len(values) or len(columns) != len(conditions):
                raise Exception('param error')

            for i in range(len(columns)):
                column = columns[i]
                value = values[i]
                condition = conditions[i]
                if condition == ConditionTypes.Greater:
                    pddata = pddata.loc[pddata[column] > value]
                elif condition == ConditionTypes.Less:
                    pddata = pddata.loc[pddata[column] < value]
                elif condition == ConditionTypes.Equal:
                    pddata = pddata.loc[pddata[column] == value]
                elif condition == ConditionTypes.Not_Greater:
                    pddata = pddata.loc[pddata[column] <= value]
                elif condition == ConditionTypes.Not_Less:
                    pddata = pddata.loc[pddata[column] >= value]
                elif condition == ConditionTypes.Not_Equal:
                    pddata = pddata.loc[pddata[column] != value]
                else:
                    raise Exception('condition error')

            LogLib.logger.info('FixModifyData cmadaas_data_del_condition over')

            return pddata
        except Exception as data:
            LogLib.logger.error('FixModifyData cmadaas_data_del_condition except %s %s' % (str(params), str(data)))

            raise data

    #输入是cmadaas接口获得，转成pandas dataframe的数据，包含Datetime,Station_Id_d,Lat,Lon和数据
    #需要添加level和dtime，都是0
    def cmadaas_data_to_sta_data(self, params):
        import meteva.base as meb

        pddata = params[FixParamTypes.GridData]
        columns = params[FixParamTypes.Columns] if FixParamTypes.Columns in params else None
        seqnum = params[FixParamTypes.SeqNum] if FixParamTypes.SeqNum in params else 0

        try:
            LogLib.logger.info('FixModifyData cmadaas_data_to_sta_data start')
            if pddata.empty:
                LogLib.logger.info('FixModifyData cmadaas_data_to_sta_data over, data empty, no change')
                return pddata

            pddata['dtime'] = seqnum
            savegrd = None
            if columns is None:
                savegrd = meb.sta_data(pddata)
            else:
                savegrd = meb.sta_data(pddata, columns=columns)

            savegrd.level = 0

            if savegrd is None:
                LogLib.logger.error('FixModifyData cmadaas_data_to_sta_data error %s' % (str(params)))
            else:
                LogLib.logger.info('FixModifyData cmadaas_data_to_sta_data over')

            return savegrd
        except Exception as data:
            LogLib.logger.error('FixModifyData cmadaas_data_to_sta_data except %s %s' % (str(params), str(data)))

            raise data

    #dataframe的站点数据，转换格式
    def dataframe_sta_data_convert(self, params):
        pddata = params[FixParamTypes.GridData]
        dname = params[FixParamTypes.DName] if FixParamTypes.DName in params else None
        
        try:
            LogLib.logger.info('FixModifyData dataframe_sta_data_convert start')
            if pddata.empty:
                LogLib.logger.info('FixModifyData dataframe_sta_data_convert over, data empty, no change')
                return pddata

            pddata['time'] = pd.to_datetime(pddata['time'])
            pddata['id'] = pddata['id'].astype(int)
            i = 999999
            for d in range(len(pddata['id'])):
                if pddata['id'][d] > 900000:
                    pddata['id'][d] = i
                    i -= 1

            pddata['lon'] = pddata['lon'].astype(float)
            pddata['lat'] = pddata['lat'].astype(float)
            pddata['data0'] = pddata['data0'].apply(lambda x: np.nan if (float(x) >= 10000) else float(x))

            if dname is not None:
                pddata.name = dname

            LogLib.logger.info('FixModifyData dataframe_sta_data_convert over')

            return pddata
        except Exception as data:
            LogLib.logger.error('FixModifyData dataframe_sta_data_convert except %s %s' % (str(params), str(data)))

            raise data
        
    #dataframe的站点数据，转换格式
    def dataframe_sta_data_convert_with_dtype(self, params):
        pddata = params[FixParamTypes.GridData]
        col_data_types = params[FixParamTypes.ColDataTypes] if FixParamTypes.ColDataTypes in params else {}

        try:
            LogLib.logger.info('FixModifyData dataframe_sta_data_convert_with_dtype start')
            if pddata.empty:
                LogLib.logger.info('FixModifyData dataframe_sta_data_convert_with_dtype over, data empty, no change')
                return pddata

            for k,v in col_data_types.items():
                if v is int:
                    pddata[k] = pddata[k].astype(int)
                elif v is float:
                    pddata[k] = pddata[k].astype(float)
                elif v is datetime:
                    pddata[k] = pd.to_datetime(pddata[k])
                else:
                    raise Exception('unknown data type')

            LogLib.logger.info('FixModifyData dataframe_sta_data_convert_with_dtype over')

            return pddata
        except Exception as data:
            LogLib.logger.error('FixModifyData dataframe_sta_data_convert_with_dtype except %s %s' % (str(params), str(data)))

            raise data
        
    #dataframe的站点数据，转换格式
    def dataframe_sta_data_convert_win(self, params):
        pddata = params[FixParamTypes.GridData]
        dname = params[FixParamTypes.DName] if FixParamTypes.DName in params else None
        
        try:
            LogLib.logger.info('FixModifyData dataframe_sta_data_convert_win start')
            if pddata.empty:
                LogLib.logger.info('FixModifyData dataframe_sta_data_convert_win over, data empty, no change')
                return pddata

            pddata['time'] = pd.to_datetime(pddata['time'])
            pddata['id'] = pddata['id'].astype(int)
            i = 999999
            for d in range(len(pddata['id'])):
                if pddata['id'][d] > 900000:
                    pddata['id'][d] = i
                    i -= 1

            pddata['lon'] = pddata['lon'].astype(float)
            pddata['lat'] = pddata['lat'].astype(float)
            pddata['speed'] = pddata['speed'].apply(lambda x: np.nan if (float(x) >= 10000) else float(x))
            pddata['direction'] = pddata['direction'].apply(lambda x: np.nan if (float(x) >= 10000) else float(x))
            
            if dname is not None:
                pddata.name = dname

            LogLib.logger.info('FixModifyData dataframe_sta_data_convert_win over')

            return pddata
        except Exception as data:
            LogLib.logger.error('FixModifyData dataframe_sta_data_convert_win except %s %s' % (str(params), str(data)))

            raise data

    #从grib2读的xarray.dataset，转换成meteva的格点数据
    def grib2_griddata_to_meteva_griddata(self, params):
        import meteva.base as meb

        ds = params[FixParamTypes.GridData]
        grid0 = params[FixParamTypes.GridR] if FixParamTypes.GridR in params else None
        sname = params[FixParamTypes.SName]
        dname = params[FixParamTypes.DName]
        default = params[FixParamTypes.Default] if FixParamTypes.Default in params else None
        delta = params[FixParamTypes.TZ_Delta] if FixParamTypes.TZ_Delta in params else None
        multi = params[FixParamTypes.Multi] if FixParamTypes.Multi in params else 1
        decimals = params[FixParamTypes.Decimals] if FixParamTypes.Decimals in params else None

        try:
            LogLib.logger.info('FixModifyData dataframe_sta_data_convert start')
            if default is not None:
                ds[sname].values[np.isnan(ds[sname].values)] = default

            dt = datetime.datetime.utcfromtimestamp(ds['time'].values.astype(datetime.datetime)*multi)
            if delta is not None:
                dt += datetime.timedelta(hours = delta)

            glon = None
            glat = None
            if grid0 is None:
                if decimals is None:
                    raise Exception('decimals is None')

                dslon = ds['longitude']
                slon = round(dslon[0].values.item(), decimals[0])
                elon = round(dslon[-1].values.item(), decimals[0])
                dlon = round(dslon[1].values.item() - dslon[0].values.item(), decimals[0])
                glon = [slon, elon, dlon]

                dslat = ds['latitude']
                slat = round(dslat[0].values.item(), decimals[1])
                elat = round(dslat[-1].values.item(), decimals[1])
                dlat = round(dslat[1].values.item() - dslat[0].values.item(), decimals[1])
                glat = [slat, elat, dlat]
            else:
                glon = grid0.glon
                glat = grid0.glat

            grid_info = meb.grid(glon, glat, gtime=[dt.strftime('%Y%m%d%H%M')])
            griddata = meb.grid_data(grid_info, ds[sname].values)
            griddata.name = dname
            griddata['lat'] = griddata['lat'].astype(np.float32)
            griddata['lon'] = griddata['lon'].astype(np.float32)
            griddata['level'] = griddata['level'].astype(np.float32)
            griddata['dtime'] = griddata['dtime'].astype(np.float32)

            return griddata
        except Exception as data:
            LogLib.logger.error('FixModifyData dataframe_sta_data_convert except %s %s' % (str(params), str(data)))

            raise data
        
    #使用dropna函数，数据可以是dataframe或者其他有dropna函数可以删除nan数据的类型。
    #通过日志输出nan的数量
    def drop_nan(self, params):
        grd = params[FixParamTypes.GridData]

        try:
            LogLib.logger.info('FixModifyData drop_nan start')
            
            allcount = len(grd)
            grd = grd.dropna()
            nancount = allcount - len(grd)

            LogLib.logger.info('FixModifyData drop_nan over.nan:%d' % (nancount))

            return grd
        except Exception as data:
            LogLib.logger.error('FixModifyData drop_nan except:%s' % (str(data)))

            raise data
        
    #统计非气象站点，通过日志输出。
    def stat_sta_not_met(self, params):
        grd = params[FixParamTypes.GridData]
        
        try:
            LogLib.logger.info('FixModifyData stat_sta_not_met start')
            
            if grd.empty:
                LogLib.logger.info('FixModifyData stat_sta_not_met over, data empty, no change. not met:0')
                return grd

            stacount = len(grd['id'][grd['id'] >= 900000])

            LogLib.logger.info('FixModifyData stat_sta_not_met over. not met:%d' % (stacount))

            return grd
        except Exception as data:
            LogLib.logger.error('FixModifyData stat_sta_not_met except:%s' % (str(data)))

            raise data
        
    #设置数据的时间
    def set_data_datetime(self, params):
        grd = params[FixParamTypes.GridData]
        dt = params[FixParamTypes.DT]
        
        try:
            LogLib.logger.info('FixModifyData set_data_datetime start')
            
            grd['time'] = dt

            LogLib.logger.info('FixModifyData set_data_datetime over.')

            return grd
        except Exception as data:
            LogLib.logger.error('FixModifyData set_data_datetime except:%s' % (str(data)))

            raise data

    def cassandra_sta_bytearray_to_m1str(self, params):
        from cassandra import sta_bytearray_to_m1str

        byteArray = params[FixParamTypes.GridData]
        columns = params[FixParamTypes.Columns]
        values = params[FixParamTypes.Values]
        fname = params[FixParamTypes.FileName]
        dt = params[FixParamTypes.DT] if FixParamTypes.DT in params else None
        tz_delta = params[FixParamTypes.TZ_Delta] if FixParamTypes.TZ_Delta in params else 0
        formatters = params[FixParamTypes.Formatters] if FixParamTypes.Formatters in params else {}

        try:
            LogLib.logger.info('FixModifyData cassandra_sta_bytearray_to_m1str start')

            rst = sta_bytearray_to_m1str(byteArray, columns, values, fname, dt, tz_delta, formatters)
            if rst is None:
                LogLib.logger.error('FixModifyData cassandra_sta_bytearray_to_m1str sta_bytearray_to_m1str error')
                return None
            else:
                LogLib.logger.info('FixModifyData cassandra_sta_bytearray_to_m1str over')
                return rst
        except Exception as data:
            LogLib.logger.error('FixModifyData cassandra_sta_bytearray_to_m1str except:%s' % (str(data)))

            raise data

    def grads_data_mean(self, params):
        (ds, ctl) = params[FixParamTypes.GridData]
        usearound = params[FixParamTypes.UseAround] if FixParamTypes.UseAround in params else False
        decimals = params[FixParamTypes.Decimals] if FixParamTypes.Decimals in params else 6

        try:
            LogLib.logger.info('FixModifyData grads_data_mean start')
            
            dsavg = {}
            for k, v in ds.items():
                dsavg[k] = np.zeros((ctl.tdef.length(), ctl.zdef.length(), ctl.ydef.length(), ctl.xdef.length()), dtype=np.float32)

                for i in range(ctl.tdef.length()):
                    for j in range(ctl.zdef.length()):
                        for m in range(ctl.ydef.length()):
                            for n in range(ctl.xdef.length()):
                                d = v[...,i,j,m,n]
                                if usearound:
                                    dsavg[k][i][j][m][n] = d[np.around(d, decimals=decimals) != ctl.undef].mean()
                                else:
                                    dsavg[k][i][j][m][n] = d[d != ctl.undef].mean()

            LogLib.logger.info('FixModifyData grads_data_mean over')

            return (dsavg, ctl)
        except Exception as data:
            LogLib.logger.error('FixModifyData grads_data_mean except:%s' % (str(data)))

            raise data
        
    #stadata：meteva格式站点数据，statinfo：pandas 第一列为站点id，用stainfos[0]访问
    def filter_data_with_stations(self, params):
        grd = params[FixParamTypes.GridDataList]
        stainfos = params[FixParamTypes.StaInfos]

        try:
            LogLib.logger.info('FixModifyData filter_data_with_stations start')
            
            rst = grd[grd['id'].isin(stations[0])].reset_index()

            LogLib.logger.info('FixModifyData filter_data_with_stations over')
            return rst
        except Exception as data:
            LogLib.logger.error('FixModifyData filter_data_with_stations except %s %s' % (str(params), str(data)))

            raise data
        
    #dataframe的站点数据，排序
    def dataframe_sta_data_sort(self, params):
        pddata = params[FixParamTypes.GridData]
        columns = params[FixParamTypes.Columns]
        ascending = params[FixParamTypes.Ascending] if FixParamTypes.Ascending in params else True
        
        try:
            LogLib.logger.info('FixModifyData dataframe_sta_data_sort start')
            if pddata.empty:
                LogLib.logger.info('FixModifyData dataframe_sta_data_sort over, data empty, no change')
                return pddata
            
            if columns is None or len(columns) == 0:
                LogLib.logger.info('FixModifyData dataframe_sta_data_sort over, columns empty, no change')
                return pddata
            
            pddata = pddata.sort_values(by=columns, ascending=ascending)
            
            LogLib.logger.info('FixModifyData dataframe_sta_data_sort over')

            return pddata
        except Exception as data:
            LogLib.logger.error('FixModifyData dataframe_sta_data_sort except %s %s' % (str(params), str(data)))

            raise data

if __name__ == '__main__':
    print('done')
