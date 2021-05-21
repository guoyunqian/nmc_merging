#!/usr/bin/python
# -*- coding: utf-8 -*-
#Filename: get_grid.py

'''
Created on May 17, 2021

@author: anduin
'''

import datetime
import xarray as xr
import numpy as np

from publictype.fixparamtypes import FixParamTypes

def reset(grd):
    lats = grd["lat"].values

    if lats[0]>lats[1]:
        lats = grd["lat"].values[::-1]
        grd['lat'] = lats
        dat = grd.values[:, :, :, :, ::-1, :]
        grd.values = dat

    return

def get_grid_from_datas(dstdatas, dt, seqobj, datas, fhsdelta):
    rst = True

    for curseq in seqobj:
        if curseq in dstdatas:
            continue

        srcseq = curseq + fhsdelta
        if srcseq in datas:
            dstdatas[curseq] = datas[srcseq]
            dstdatas[curseq]['dtime'] = curseq
            dstdatas[curseq]['time'] = dt
        else:
            rst =  False
            
    return rst

def get_grid_missing(dt, nlon, nlat, slon, slat, elon, elat, dlon, dlat, level=0, seq=None, miss_value=9999., data_name = "data0", scale_decimals=2):
    if round((nlon-1) * dlon + 0.1**(scale_decimals+1), scale_decimals) != round(elon - slon + 0.1**(scale_decimals+2)) \
        or round((nlat-1) * dlat + 0.1**(scale_decimals+1), scale_decimals) != round(elat - slat + 0.1**(scale_decimals+2)):
        raise Exception('lon lat infos error')

    if seq is None:
        seq = dt.hour

    dat = np.full(nlat*nlon, miss_value).astype(float).reshape((1, 1, 1, 1, nlat, nlon))
    
    lon = np.arange(nlon) * dlon + slon
    lat = np.arange(nlat) * dlat + slat

    da = xr.DataArray(dat, coords={'member': [data_name], 'level': [level], 'time': [dt], 'dtime': [seq], 'lat': lat, 'lon': lon},
                      dims=['member', 'level', 'time', 'dtime', 'lat', 'lon'])
    da.attrs["dtime_type"] = "hour"
    #da.name = "data0"

    return da

def get_grid_from_grib(grb, dt, seq=None, level_field=None, data_name="data0"):
    if seq is None:
        seq = dt.hour

    if level_field is None:
        level = 0
    else:
        level = grb[level_field]
        
    lon = np.arange(grb.Ni) * grb.iDirectionIncrementInDegrees + grb.longitudeOfFirstGridPointInDegrees
    lat = np.arange(grb.Nj) * grb.jDirectionIncrementInDegrees + grb.latitudeOfFirstGridPointInDegrees

    ds = np.array(grb.values) if type(grb.values) == np.ma.core.MaskedArray else grb.values
    da = xr.DataArray(ds.reshape((1,1,1,1,grb.Nj,grb.Ni)), coords={'member': [data_name], 'level': [level], 'time': [dt], 'dtime': [seq], 'lat': lat, 'lon': lon},
                      dims=['member', 'level', 'time', 'dtime', 'lat', 'lon'])
    da.attrs["dtime_type"] = "hour"
    #da.name = "data0"

    return da

def get_grid_from_grib_file(fread, filename, dt, seq, seq_field=None, level_field=None, data_name='data0', gribrst=True, seq_key_is_num=False):
    params = {}
    params[FixParamTypes.SFullPath] = filename
    params[FixParamTypes.SeqObj] = seq
    params[FixParamTypes.SeqField] = seq_field
    params[FixParamTypes.SeqKeyIsNum] = seq_key_is_num

    rsts = fread.read_gribdata_from_grib2_with_pygrib_single_file_seqnum(params)

    if rsts is None or len(rsts) == 0:
        return rsts

    grds = {}
    for k,v in rsts.items():
        curseq = int(k)
        if gribrst:
            grds[curseq] = v
        else:
            grds[curseq] = get_grid_from_grib(v, dt, seq=curseq, level_field=level_field, data_name=data_name)

    return grds

if __name__ == '__main__':
    print(get_dts_withec(datetime.datetime.now(), 20))

    print('test done')


