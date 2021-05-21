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

from publictype.fixparamtypes import FixParamTypes

class FixModifyData(object):
    #如果数据是xarray，当前只支持单数据，名字为tp。
    def eliminate_grid_nan(self, params):
        gdata = params[FixParamTypes.GridData]
        default = params[FixParamTypes.Default]
        deepcopy = params[FixParamTypes.DeepCopy]

        try:
            #LogLib.logger.info('FixModifyData eliminate_grid_nan start')
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

            #LogLib.logger.info('FixModifyData eliminate_grid_nan over')

            return gdata
        except Exception as data:
            #LogLib.logger.error('FixModifyData eliminate_grid_nan except:%s' % (str(data)))

            raise data
            
    def eliminate_grid_missdata(self, params):
        grd = params[FixParamTypes.GridData]
        miss = params[FixParamTypes.Miss]
        default = params[FixParamTypes.Default]
        usearound = params[FixParamTypes.UseAround]
        decimals = params[FixParamTypes.Decimals]
        deepcopy = params[FixParamTypes.DeepCopy]

        try:
            #LogLib.logger.info('FixModifyData eliminate_grid_missdata start')
            if deepcopy:
                grd.values = copy.deepcopy(grd.values)

            a = grd.values
            if usearound:
                a[np.around(a, decimals=decimals) == miss] = default
            else:
                a[a==miss] = default

            #LogLib.logger.info('FixModifyData eliminate_grid_missdata over')

            return grd
        except Exception as data:
            #LogLib.logger.error('FixModifyData eliminate_grid_missdata except:%s' % (str(data)))

            raise data

    def interp_gg_linear(self, params):
        import meteva.base as meb

        grd = params[FixParamTypes.GridData]
        grid = params[FixParamTypes.GridW]
        outer_value = params[FixParamTypes.Default]
        
        try:
            #LogLib.logger.info('FixModifyData interp_gg_linear start')
            savegrd = meb.interp_gg_linear(grd, grid, outer_value=outer_value)
            if savegrd is None:
                #LogLib.logger.error('FixModifyData interp_gg_linear error %s' % (str(params)))
                return savegrd
            else:
                #LogLib.logger.info('FixModifyData interp_gg_linear over')
                pass

            return savegrd
        except Exception as data:
            #LogLib.logger.error('FixModifyData interp_gg_linear except %s %s' % (str(params), str(data)))

            raise data

    def change_gird_data_dtype(self, params):
        grd = params[FixParamTypes.GridData]
        dname = params[FixParamTypes.DName]
        s_dtype = params[FixParamTypes.S_DType]
        d_dtype = params[FixParamTypes.D_DType]
        keep_attrs = params[FixParamTypes.KeepAttrs] if FixParamTypes.KeepAttrs in params else True

        try:
            #LogLib.logger.info('FixModifyData change_gird_data_dtype start')
            oritype = grd[dname].dtype
            if oritype != s_dtype:
                if oritype == d_dtype:
                    #LogLib.logger.info('FixModifyData change_gird_data_dtype no change')
                    return grd
                else:
                    raise Exception('dtype error %s' % str(oritype))

            attrs = None
            if keep_attrs:
                attrs = grd[dname].attrs

            grd[dname] = grd[dname].astype(d_dtype)

            if keep_attrs and attrs is not None:
                grd[dname].attrs = attrs

            #LogLib.logger.info('FixModifyData change_gird_data_dtype over')

            return grd
        except Exception as data:
            #LogLib.logger.error('FixModifyData change_gird_data_dtype except %s %s' % (str(params), str(data)))

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
            #LogLib.logger.info('FixModifyData dataframe_sta_data_convert start')
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
            #LogLib.logger.error('FixModifyData dataframe_sta_data_convert except %s %s' % (str(params), str(data)))

            raise data
        
    #使用dropna函数，数据可以是dataframe或者其他有dropna函数可以删除nan数据的类型。
    #通过日志输出nan的数量
    def drop_nan(self, params):
        grd = params[FixParamTypes.GridData]

        try:
            #LogLib.logger.info('FixModifyData drop_nan start')
            
            allcount = len(grd)
            grd = grd.dropna()
            nancount = allcount - len(grd)

            #LogLib.logger.info('FixModifyData drop_nan over.nan:%d' % (nancount))

            return grd
        except Exception as data:
            #LogLib.logger.error('FixModifyData drop_nan except:%s' % (str(data)))

            raise data
        
    #设置数据的时间
    def set_data_datetime(self, params):
        grd = params[FixParamTypes.GridData]
        dt = params[FixParamTypes.DT]
        
        try:
            #LogLib.logger.info('FixModifyData set_data_datetime start')
            
            grd['time'] = dt

            #LogLib.logger.info('FixModifyData set_data_datetime over.')

            return grd
        except Exception as data:
            #LogLib.logger.error('FixModifyData set_data_datetime except:%s' % (str(data)))

            raise data

if __name__ == '__main__':
    print('done')
