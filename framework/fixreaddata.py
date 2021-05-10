#!/usr/bin/python
# -*- coding: utf-8 -*-
#Filename: fixreaddata.py

'''
Created on Aug 21, 2020

@author: anduin
'''

import os
import numpy as np
import json
import datetime
import pandas as pd
import xarray
import time

from logmodule.loglib import *
from publictype.fixparamtypes import FixParamTypes

class FixReadData(object):
    def read_xarraydata_from_nc(self, params):
        from_file = params[FixParamTypes.SFullPath]

        try:
            LogLib.logger.info('FixReadData read_xarraydata_from_nc start %s' % (str(params)))

            xdata = xarray.open_dataset(from_file)
            if xdata is None:
                LogLib.logger.error('FixReadData read_xarraydata_from_nc read error %s' % (str(params)))
            else:
                LogLib.logger.info('FixReadData read_xarraydata_from_nc over')

            return xdata
        except Exception as data:
            LogLib.logger.error('FixReadData read_xarraydata_from_nc except %s %s' % (str(params), str(data)))

            raise data
        
    def read_griddata_from_nc(self, params):
        import meteva.base as meb

        from_file = params[FixParamTypes.SFullPath]
        grid = params[FixParamTypes.GridR] if FixParamTypes.GridR in params else None
        dname = params[FixParamTypes.DName] if FixParamTypes.DName in params else None

        try:
            LogLib.logger.info('FixReadData read_griddata_from_nc start %s' % (str(params)))
            
            grd = None
            if grid is None:
                grd = meb.read_griddata_from_nc(filename=from_file)
            else:
                grd = meb.read_griddata_from_nc(filename=from_file, grid=grid)

            if grd is None:
                LogLib.logger.error('FixReadData read_griddata_from_nc read error %s' % (str(params)))
            else:
                if dname is not None and len(dname) > 0:
                    grd.name = dname

                LogLib.logger.info('FixReadData read_griddata_from_nc over')

            return grd
        except Exception as data:
            LogLib.logger.error('FixReadData read_griddata_from_nc except %s %s' % (str(params), str(data)))

            raise data
        
    def read_griddata_from_bin(self, params):
        import meteva.base as meb

        from_file = params[FixParamTypes.SFullPath]
        curdtype = params[FixParamTypes.DType]
        nlon = params[FixParamTypes.NLon]
        nlat = params[FixParamTypes.NLat]
        multi = params[FixParamTypes.Multi]
        grid = params[FixParamTypes.GridR]

        try:
            LogLib.logger.info('FixReadData read_griddata_from_bin start %s' % (str(params)))

            grd = None

            datalen = -1  #nlon * nlat
            curdata = np.fromfile(from_file, dtype=curdtype, count=datalen)
            if datalen != -1 and len(curdata) != datalen:
                LogLib.logger.error('FixReadData read_griddata_from_bin data len error %s' % (str(params)))
                return grd

            curdata.resize(nlat, nlon)

            if multi is not None:
                curdata = curdata * multi

            grd = meb.grid_data(grid, data=curdata)
            meb.reset(grd)
            
            return grd
        except Exception as data:
            LogLib.logger.error('FixReadData read_griddata_from_bin except %s %s' % (str(params), str(data)))

            raise data
        
    def read_griddata_from_micaps4(self, params):
        import meteva.base as meb

        from_file = params[FixParamTypes.SFullPath]
        grid = params[FixParamTypes.GridR] if FixParamTypes.GridR in params else None

        try:
            LogLib.logger.info('FixReadData read_griddata_from_micaps4 start %s' % (str(params)))

            grd = None
            if grid is None:
                grd = meb.read_griddata_from_micaps4(filename=from_file)
            else:
                grd = meb.read_griddata_from_micaps4(filename=from_file, grid=grid)

            if grd is None:
                LogLib.logger.error('FixReadData read_griddata_from_micaps4 read error %s' % (str(params)))
            else:
                LogLib.logger.info('FixReadData read_griddata_from_micaps4 over')

            return grd
        except Exception as data:
            LogLib.logger.error('FixReadData read_griddata_from_micaps4 except %s %s' % (str(params), str(data)))

            raise data
            
    
    def read_griddata_from_gds_bz2_onlyone(self, params):
        import bz2
        from meteva.base.io.GDS_data_service import GDSDataService
        from meteva.base.io import DataBlock_pb2
        import meteva.base as meb
        from cassandra import read_SWAN_d131_to_grid

        from_file = params[FixParamTypes.SFullPath]
        seq_proc = params[FixParamTypes.SeqProc]
        grid = params[FixParamTypes.GridR]
        is_url = params[FixParamTypes.IsUrl] if FixParamTypes.IsUrl in params else True
        srv_ip = params[FixParamTypes.SrvIP] if FixParamTypes.SrvIP in params else None
        srv_port = params[FixParamTypes.SrvPort] if FixParamTypes.SrvPort in params else None

        try:
            LogLib.logger.info('FixReadData read_griddata_from_gds_bz2_onlyone start %s' % (str(params)))
            dir, fname = os.path.split(from_file)
            seqnum = seq_proc(fname)
            bz2data = None

            if is_url:
                service = GDSDataService(gdsIp=srv_ip, gdsPort=srv_port)

                status, response = service.getData(dir, fname)
                if status != 200:
                    LogLib.logger.error('FixReadData read_griddata_from_gds_bz2_onlyone getData error %s' % (str(params)))
                    return None

                barst = DataBlock_pb2.ByteArrayResult()
                if barst is None:
                    LogLib.logger.error('FixReadData read_griddata_from_gds_bz2_onlyone ByteArrayResult error %s' % (str(params)))
                    return None
            
                barst.ParseFromString(response)
                if barst.errorCode != 0:
                    LogLib.logger.error('FixReadData read_griddata_from_gds_bz2_onlyone ByteArrayResult error %d %s %s' % (barst.errorCode, barst.errorMessage, str(params)))
                    return None

                bz2data = barst.byteArray
            else:
                with open(from_file, 'rb') as f:
                    bz2data = f.read()
                
            if bz2data is None:
                LogLib.logger.error('FixReadData read_griddata_from_gds_bz2_onlyone read error %s' % (str(params)))
                return None

            byteArray = bz2.decompress(bz2data)

            grd = read_SWAN_d131_to_grid(byteArray, seqnum)
            
            if grd is None:
                LogLib.logger.error('FixReadData read_griddata_from_gds_bz2_onlyone read error %s' % (str(params)))
                return None

            a = np.squeeze(grd.data.values)
            grd_data_bin = meb.grid_data(grid,data=a)

            LogLib.logger.info('FixReadData read_griddata_from_gds_bz2_onlyone over')

            return grd_data_bin
        except Exception as data:
            LogLib.logger.error('FixReadData read_griddata_from_gds_bz2_onlyone except %s %s' % (str(params), str(data)))

            return None
            
    def read_data_from_gds(self, params):
        from meteva.base.io.GDS_data_service import GDSDataService
        from meteva.base.io import DataBlock_pb2

        from_file = params[FixParamTypes.SFullPath]
        is_url = params[FixParamTypes.IsUrl] if FixParamTypes.IsUrl in params else True
        srv_ip = params[FixParamTypes.SrvIP] if FixParamTypes.SrvIP in params else None
        srv_port = params[FixParamTypes.SrvPort] if FixParamTypes.SrvPort in params else None

        try:
            LogLib.logger.info('FixReadData read_data_from_gds start %s' % (str(params)))
            dir, fname = os.path.split(from_file)
            bz2data = None

            if is_url:
                service = GDSDataService(gdsIp=srv_ip, gdsPort=srv_port)

                status, response = service.getData(dir, fname)
                if status != 200:
                    LogLib.logger.error('FixReadData read_data_from_gds getData error %s' % (str(params)))
                    return None

                barst = DataBlock_pb2.ByteArrayResult()
                if barst is None:
                    LogLib.logger.error('FixReadData read_data_from_gds ByteArrayResult error %s' % (str(params)))
                    return None
            
                barst.ParseFromString(response)
                if barst.errorCode != 0:
                    LogLib.logger.error('FixReadData read_data_from_gds ByteArrayResult error %d %s %s' % (barst.errorCode, barst.errorMessage, str(params)))
                    return None

                bz2data = barst.byteArray
            else:
                with open(from_file, 'rb') as f:
                    bz2data = f.read()
                
            if bz2data is None:
                LogLib.logger.error('FixReadData read_data_from_gds read error %s' % (str(params)))
                return None

            LogLib.logger.info('FixReadData read_data_from_gds over')

            return bz2data
        except Exception as data:
            LogLib.logger.error('FixReadData read_data_from_gds except %s %s' % (str(params), str(data)))

            return None
            '''
    def read_griddata_from_gds(self, params):
        import meteva.base as meb

        from_file = params[FixParamTypes.SFullPath]
        is_url = params[FixParamTypes.IsUrl] if FixParamTypes.IsUrl in params else True
        srv_ip = params[FixParamTypes.SrvIP] if FixParamTypes.SrvIP in params else None
        srv_port = params[FixParamTypes.SrvPort] if FixParamTypes.SrvPort in params else None

        try:
            LogLib.logger.info('FixReadData read_griddata_from_gds start %s' % (str(params)))
            if meb.gds_ip_port is None:
                meb.gds_ip_port = (srv_ip, srv_port)
                
            grd = None

            if is_url:
                grd = meb.read_griddata_from_gds(from_file)
            else:
                grd = meb.read_griddata_from_gds_file(from_file)

            LogLib.logger.info('FixReadData read_griddata_from_gds over')

            return grd
        except Exception as data:
            LogLib.logger.error('FixReadData read_griddata_from_gds except %s %s' % (str(params), str(data)))

            return None
            '''
            
    def read_griddata_from_gds(self, params):
        import cassandra.decoder_meteva as cdm

        from_file = params[FixParamTypes.SFullPath]
        is_url = params[FixParamTypes.IsUrl] if FixParamTypes.IsUrl in params else True
        srv_ip = params[FixParamTypes.SrvIP] if FixParamTypes.SrvIP in params else None
        srv_port = params[FixParamTypes.SrvPort] if FixParamTypes.SrvPort in params else None
        user_nmem = params[FixParamTypes.UserNMem] if FixParamTypes.UserNMem in params else -1

        try:
            LogLib.logger.info('FixReadData read_griddata_from_gds start %s' % (str(params)))

            grd = None

            if is_url:
                grd = cdm.read_griddata_from_gds(srv_ip, srv_port, from_file, user_nmem=user_nmem)
            else:
                grd = cdm.read_griddata_from_gds_file(from_file, user_nmem=user_nmem)

            LogLib.logger.info('FixReadData read_griddata_from_gds over')

            return grd
        except Exception as data:
            LogLib.logger.error('FixReadData read_griddata_from_gds except %s %s' % (str(params), str(data)))

            return None

    def read_gridwind_from_gds(self, params):
        import meteva.base as meb

        from_file = params[FixParamTypes.SFullPath]
        is_url = params[FixParamTypes.IsUrl] if FixParamTypes.IsUrl in params else True
        srv_ip = params[FixParamTypes.SrvIP] if FixParamTypes.SrvIP in params else None
        srv_port = params[FixParamTypes.SrvPort] if FixParamTypes.SrvPort in params else None

        try:
            LogLib.logger.info('FixReadData read_gridwind_from_gds start %s' % (str(params)))
            if meb.gds_ip_port is None:
                meb.gds_ip_port = (srv_ip, srv_port)
                
            grd = None

            if is_url:
                grd = meb.read_gridwind_from_gds(from_file)
            else:
                grd = meb.read_griddata_from_gds_file(from_file)

            LogLib.logger.info('FixReadData read_gridwind_from_gds over')

            return grd
        except Exception as data:
            LogLib.logger.error('FixReadData read_gridwind_from_gds except %s %s' % (str(params), str(data)))

            return None
            
    #从cmadaas获得json格式数据，使用json库解析，构建一个dataframe返回。
    def read_data_from_cmadaas(self, params):
        from CMADaas.CMADaasAccess import CMADaasAccess
        from CMADaas.CMADaasError import CMADaasError

        dt = params[FixParamTypes.DT]
        url = params[FixParamTypes.Url]
        urlparams = params[FixParamTypes.UrlParams]
        time_proc = params[FixParamTypes.TimeProc]
        columns = params[FixParamTypes.Columns] if FixParamTypes.Columns in params else None

        try:
            LogLib.logger.info('FixReadData read_data_from_cmadaas start %s' % (str(params)))
            
            urlparams['timestamp'] = str(int(datetime.datetime.now().timestamp()*1000))
            urlparams = time_proc(dt, urlparams, deep_copy=True)

            fullurl = CMADaasAccess.get_url(url, urlparams)
            if fullurl is None:
                return None
            
            cmarst = CMADaasAccess.read_data(fullurl)
            if cmarst[0] == CMADaasError.NetError:
                time.sleep(CMADaasAccess.neterr_interval)
                cmarst = CMADaasAccess.read_data(fullurl)
            elif cmarst[0] == CMADaasError.MinLimited:
                time.sleep(CMADaasAccess.minlimited_interval)
                cmarst = CMADaasAccess.read_data(fullurl)

            rst = cmarst[1]
            if rst is None:
                return None

            pddata = pd.DataFrame.from_dict(rst)
            if pddata is None:
                LogLib.logger.error('FixReadData read_data_from_cmadaas pandas dataframe from_dict error %s %s' % (str(rst), str(params)))
            else:
                if columns is not None:
                    pddata.columns = columns

                LogLib.logger.info('FixReadData read_data_from_cmadaas over %s' % (str(fullurl)))

            return pddata
        except Exception as data:
            LogLib.logger.error('FixReadData read_data_from_cmadaas except %s %s' % (str(params), str(data)))

            return None
            
    #从cmadaas获得json格式的数据，构建一个meteva格点数据返回。
    def read_griddata_from_cmadaas(self, params):
        import meteva.base as meb
        from CMADaas.CMADaasAccess import CMADaasAccess
        from CMADaas.CMADaasError import CMADaasError

        dt = params[FixParamTypes.DT]
        url = params[FixParamTypes.Url]
        urlparams = params[FixParamTypes.UrlParams]
        time_proc = params[FixParamTypes.TimeProc]

        try:
            LogLib.logger.info('FixReadData read_griddata_from_cmadaas start %s' % (str(params)))
            
            urlparams['timestamp'] = str(int(datetime.datetime.now().timestamp()*1000))
            urlparams = time_proc(dt, urlparams, deep_copy=True)

            fullurl = CMADaasAccess.get_url(url, urlparams)
            if fullurl is None:
                return None
            
            cmarst = CMADaasAccess.read_grid_and_data(fullurl)
            if cmarst[0] == CMADaasError.NetError:
                time.sleep(CMADaasAccess.neterr_interval)
                cmarst = CMADaasAccess.read_grid_and_data(fullurl)
            elif cmarst[0] == CMADaasError.MinLimited:
                time.sleep(CMADaasAccess.minlimited_interval)
                cmarst = CMADaasAccess.read_grid_and_data(fullurl)

            rst = cmarst[1]
            if rst is None:
                return None

            if len(rst) == 0:
                LogLib.logger.error('FixReadData read_griddata_from_cmadaas no data %s' % (str(params)))
                return None

            lonS = round(rst[1][0], 4)
            latS = round(rst[1][1], 4)
            dlon = round(rst[1][2], 4)
            dlat = round(rst[1][3], 4)
            nlon = int(rst[1][4])
            nlat = int(rst[1][5])
            lonE = lonS + (nlon-1)*dlon
            latE = latS + (nlat-1)*dlat

            data = np.array(rst[0])
            dtime = [int(urlparams['validTime'])]
            grid_info = meb.grid([lonS,lonE,dlon],[latS,latE,dlat],gtime =[dt],dtime_list=dtime)
            griddata = meb.grid_data(grid_info, data)

            if griddata is None:
                LogLib.logger.error('FixReadData read_griddata_from_cmadaas pandas grid_data error %s %s' % (str(rst), str(params)))
            else:
                LogLib.logger.info('FixReadData read_griddata_from_cmadaas over %s' % (str(fullurl)))

            return griddata
        except Exception as data:
            LogLib.logger.error('FixReadData read_griddata_from_cmadaas except %s %s' % (str(params), str(data)))

            return None
            
    #从cmadaas获得文件数据。
    def read_file_from_cmadaas(self, params):
        from CMADaas.CMADaasAccess import CMADaasAccess
        from CMADaas.CMADaasError import CMADaasError

        fullurl = params[FixParamTypes.SFullPath]

        try:
            LogLib.logger.info('FixReadData read_file_from_cmadaas start %s' % (str(params)))

            cmarst = CMADaasAccess.read_file(fullurl)
            if cmarst[0] == CMADaasError.NetError:
                time.sleep(CMADaasAccess.neterr_interval)
                cmarst = CMADaasAccess.read_file(fullurl)

            rst = cmarst[1]
            if rst is None:
                return None
            else:
                return rst
        except Exception as data:
            LogLib.logger.error('FixReadData read_file_from_cmadaas except %s %s' % (str(params), str(data)))

            return None
            
    def read_data_from_h5(self, params):
        from_file = params[FixParamTypes.SFullPath]

        try:
            LogLib.logger.info('FixReadData read_data_from_h5 start %s' % (str(params)))

            return pd.read_hdf(from_file)
        except Exception as data:
            LogLib.logger.error('FixReadData read_data_from_h5 except %s %s' % (str(params), str(data)))

            return None
            
    def read_data_from_caiyun_h5(self, params):
        import meteva.base as meb

        from_file = params[FixParamTypes.SFullPath]
        fhour = params[FixParamTypes.FHS]
        staid = params[FixParamTypes.StaID]
        lon = params[FixParamTypes.SLon]
        lat = params[FixParamTypes.SLat]
        dt = params[FixParamTypes.DT]
        delta = params[FixParamTypes.TZ_Delta]

        try:
            LogLib.logger.info('FixReadData read_data_from_caiyun_h5 start %s' % (str(params)))

            temp_data = pd.read_hdf(from_file)
            df1 = temp_data.iloc[(fhour[0]-1):len(fhour),0:2]
            df1['id'] = staid
            df1['lon'] = lon
            df1['lat'] = lat
            df1['dtime'] = fhour
            df1['datetime'] = dt + datetime.timedelta(hours=delta)
            sta = meb.sta_data(df1, columns=['time','data0','id','lon','lat','dtime'])
            sta.level = 0

            return sta
        except Exception as data:
            LogLib.logger.error('FixReadData read_data_from_caiyun_h5 except %s %s' % (str(params), str(data)))

            return None
        
    def read_data_from_txt(self, params):
        import meteva.base as meb

        dt = params[FixParamTypes.DT]
        from_file = params[FixParamTypes.SFullPath]
        rangedelta = params[FixParamTypes.RangeDelta]
        delimiter = params[FixParamTypes.SepStr]
        columns = params[FixParamTypes.Columns]
        staids = params[FixParamTypes.StaIDs]

        try:
            LogLib.logger.info('FixReadData read_data_from_caiyun_txt start %s' % (str(params)))

            all_data =  np.loadtxt(from_file, delimiter=delimiter)
            
            sta_num = len(all_data)
            dcount = len(all_data[0])
            dstart = 2  #第一个数据列是经度，第二个数据列是维度

            new_all_data = None

            dtime = 1

            for i in range(dstart, dcount, rangedelta):
                new_data = all_data[:,:dstart]
    
                #z = np.linspace(1, sta_num, sta_num, dtype=np.int32)
                #new_data = np.column_stack((new_data,z.T))
                #new_data = np.column_stack((new_data, staids.T))
    
                t = np.full((sta_num), dt)
                new_data = np.column_stack((new_data,t.T))
    
                y = np.full((sta_num), dtime)
                dtime += 1
    
                new_data = np.column_stack((new_data,y.T))
    
                x = np.zeros((sta_num), dtype=np.float)
                for j in range(rangedelta):
                    x += all_data[:, i+j]
        
                new_data = np.column_stack((new_data,x.T))
    
                if new_all_data is None:
                    new_all_data = new_data
                else:
                    new_all_data = np.row_stack((new_all_data, new_data))
    
            #print(new_all_data)
            #print(new_all_data.shape)

            df1 = pd.DataFrame(new_all_data, columns=columns[:-1])
            df3 = pd.merge(df1, staids, on=[columns[0], columns[1]], how='left')
            if len(df3[pd.isna(df3['id'])]) > 0:
                LogLib.logger.error('FixReadData read_data_from_caiyun_txt unknow id')

            sta = meb.sta_data(df3.dropna(), columns=columns)
            sta.level = 0

            sta['id'] = sta['id'].astype(np.int32)
            sta['lon'] = sta['lon'].astype(float)
            sta['lat'] = sta['lat'].astype(float)
            sta['data0'] = sta['data0'].astype(float)
            sta['dtime'] = sta['dtime'].astype(np.int32)
            sta['level'] = sta['level'].astype(np.int32)

            return sta
        except Exception as data:
            LogLib.logger.error('FixReadData read_data_from_caiyun_txt except %s %s' % (str(params), str(data)))

            return None
        
    #青海从ftp读取数据，模式数据是micaps4格点数据，需要转成nc；实况数据-micaps3站点数据，直接下载，不需要处理。
    def read_data_for_qinghai(self, params):
        from mc.Meteo_class import grid_data
        from netconn.ftpconn import FtpConn
        
        srv_ip = params[FixParamTypes.SrvIP]
        srv_port = params[FixParamTypes.SrvPort]
        srv_username = params[FixParamTypes.SrvUserName]
        srv_pwd = params[FixParamTypes.SrvPwd]
        from_file = params[FixParamTypes.SFullPath]
        ori_format = params[FixParamTypes.FileFmt] if FixParamTypes.FileFmt in params else 0
        #grd = params[FixParamTypes.File_Fmt] if FixParamTypes.File_Fmt in params else None

        griddata = params[FixParamTypes.GridData] if FixParamTypes.GridData in params else None

        conn = None
        try:
            LogLib.logger.debug('FixReadData read_data_for_qinghai start %s' % (str(params)))
            
            conn = FtpConn(srv_ip, srv_port)
            if not conn.login(srv_username, srv_pwd):
                LogLib.logger.error('FixReadData read_data_for_qinghai ftp login error %s' % (str(params)))
                return None

            rst, fdata = conn.download_file_to_buf(from_file)
            if not rst:
                LogLib.logger.error('FixReadData read_data_for_qinghai ftp download error %s' % (str(params)))
                return None

            if fdata is None:
                LogLib.logger.info('FixReadData read_data_for_qinghai ftp download data is None %s' % (str(params)))
                return None
            '''
            fdata = None
            with open(from_file, 'rb') as f:
                fdata = f.read()
                '''
            grd_ori = None
            if ori_format==0:#micaps4格式
                grd_ori = grid_data()
                grd_ori.ReadMicaps4_from_buf(fdata, show=0)#读取格点信息
            #elif ori_format==1:#bin二进制格式
            #    grd_ori = grid_data(similar_to=grd)
            #    grd_ori.ReadBin(from_file, multi=1., show=0)
            elif ori_format == 2:
                LogLib.logger.debug('FixReadData read_data_for_qinghai over %s' % (str(params)))
                return fdata
            else:
                LogLib.logger.error('FixReadData read_data_for_qinghai unknown file format %s' % (str(params)))
                return None

            if grd_ori.dlat < 0:
                grd_ori.Reverse_grid()

            if griddata is None:
                griddata = grd_ori
            else:
                grd_ori.BiLinear_inter_grd(griddata)

            LogLib.logger.debug('FixReadData read_data_for_qinghai over %s' % (str(params)))

            return griddata
        except Exception as data:
            LogLib.logger.error('FixReadData read_data_for_qinghai except %s %s' % (str(params), str(data)))

            return None
        finally:
            if conn is not None:
                conn.quit()
            #pass
            
    #云平台降水分析数据
    #backend_kwargs={'filter_by_keys':{'typeOfLevel': 'isobaricInhPa','level':500}})
    #没有过滤条件的话，只能读取一个数据集的文件
    def read_data_from_grib2(self, params):
        from_file = params[FixParamTypes.SFullPath]
        conditions = params[FixParamTypes.Conditions] if FixParamTypes.Conditions in params else None

        try:
            LogLib.logger.info('FixReadData read_data_from_grib2 start %s' % (str(params)))

            ds = None
            if conditions is None:
                ds = xarray.open_dataset(from_file, engine='cfgrib')
            else:
                ds = xarray.open_dataset(from_file, engine='cfgrib', backend_kwargs=conditions)

            LogLib.logger.info('FixReadData read_data_from_grib2 over %s' % (str(params)))

            return ds
        except Exception as data:
            LogLib.logger.error('FixReadData read_data_from_grib2 except %s %s' % (str(params), str(data)))

            return None
        
    #读单个grib2文件，输出文件的每一个grib结果数据，包括grid和数据，grib2文件中数据读出后是maskarray，将缺测值替换为numpy.nan
    #读指定的数目的grb
    def read_data_from_grib2_with_pygrib_single_file(self, params):
        from_file = params[FixParamTypes.SFullPath]
        seq_count = params[FixParamTypes.SeqCount] if FixParamTypes.SeqCount in params else None

        try:
            import pygrib
            LogLib.logger.info('FixReadData read_data_from_grib2_with_pygrib_single_file start %s' % (str(params)))

            rst = []
            grbs = pygrib.open(from_files)
            j = 0
            for grb in grbs:
                if seq_count is not None and j >= seq_count:
                    break
                else:
                    j += 1

                ds = grb.values
                ds.data[ds.data == ds.fill_value] = np.nan

                #起始纬度#终止纬度#起始经度#终止经度#经度分辨率#纬度分辨率#经度方向格点个数#纬度方向格点个数#格点场值
                rst.append([(grb.latitudeOfFirstGridPointInDegrees, grb.latitudeOfLastGridPointInDegrees,
                                grb.longitudeOfFirstGridPointInDegrees, grb.longitudeOfLastGridPointInDegrees,
                                grb.iDirectionIncrementInDegrees, grb.jDirectionIncrementInDegrees,
                                grb.Ni, grb.Nj), ds.data])

            LogLib.logger.info('FixReadData read_data_from_grib2_with_pygrib_single_file over %s' % (str(params)))
            return rst
        except Exception as data:
            LogLib.logger.error('FixReadData read_data_from_grib2_with_pygrib_single_file except %s %s' % (str(params), str(data)))

            return None
        
    #读多个grib2文件，输出所有文件的每一个grib结果数据，包括grid和数据，grib2文件中数据读出后是maskarray，将缺测值替换为numpy.nan
    #读指定的数目的grb
    def read_data_from_grib2_with_pygrib(self, params):
        from_files = params[FixParamTypes.SFullPaths]
        seq_counts = params[FixParamTypes.SeqCounts] if FixParamTypes.SeqCounts in params else None

        try:
            import copy
            LogLib.logger.info('FixReadData read_data_from_grib2_with_pygrib start %s' % (str(params)))

            sparams = copy.deepcopy(params)

            rsts = []
            for i in range(len(from_files)):
                sparams[FixParamTypes.SFullPath] = from_files[i]
                sparams[FixParamTypes.SeqCount] = seq_counts if seq_counts is None else seq_counts[i]
                rst = self.read_data_from_grib2_with_pygrib_single_file(sparams)

                rsts.append(rst)
                
            LogLib.logger.info('FixReadData read_data_from_grib2_with_pygrib over %s' % (str(params)))
            return rsts
        except Exception as data:
            LogLib.logger.error('FixReadData read_data_from_grib2_with_pygrib except %s %s' % (str(params), str(data)))

            return None
        
    #读单个grib2文件，返回文件中grib的列表
    def read_gribdata_from_grib2_with_pygrib_single_file_seq_count(self, params):
        from_file = params[FixParamTypes.SFullPath]
        seq_count = params[FixParamTypes.SeqCount] if FixParamTypes.SeqCount in params else None

        try:
            import pygrib
            LogLib.logger.info('FixReadData read_gribdata_from_grib2_with_pygrib_single_file_seq_count start %s' % (str(params)))
            
            rst = []
            grbs = pygrib.open(from_files)
            j = 0
            for grb in grbs:
                if seq_count is not None and j >= seq_count:
                    break
                else:
                    j += 1

                rst.append(grb)

            LogLib.logger.info('FixReadData read_gribdata_from_grib2_with_pygrib_single_file_seq_count over %s' % (str(params)))
            return rst
        except Exception as data:
            LogLib.logger.error('FixReadData read_gribdata_from_grib2_with_pygrib_single_file_seq_count except %s %s' % (str(params), str(data)))

            return None
    
    #读单个grib2文件，返回以seqnum为key，文件中grib为value的字典
    def read_gribdata_from_grib2_with_pygrib_single_file_seqnum(self, params):
        from publictype.gribtypes import GribTypes
        
        from_file = params[FixParamTypes.SFullPath]
        seq_and_p_num = None
        if FixParamTypes.SeqAndPNum in params:
            seq_and_p_num = params[FixParamTypes.SeqAndPNum]
        elif FixParamTypes.SeqObj in params:
            seq_and_p_num = list(map(str, params[FixParamTypes.SeqObj]))

        seqfield = params[FixParamTypes.SeqField] if FixParamTypes.SeqField in params else GribTypes.endStep
        pnumfield = params[FixParamTypes.PNumField] if FixParamTypes.PNumField in params else None   #GribTypes.perturbationNumber
        
        try:
            import pygrib
            LogLib.logger.info('FixReadData read_gribdata_from_grib2_with_pygrib_single_file_seqnum start %s' % (str(params)))
            
            rst = {}
            grbs = pygrib.open(from_file)
            for grb in grbs:
                seqnum = 0
                if seqfield == GribTypes.endStep:
                    seqnum = grb.endStep
                elif seqfield == GribTypes.stepRange:
                    seqnum = grb.stepRange
                else:
                    raise Exception('error seq field')

                pnum = 0
                if pnumfield == None:
                    pass
                elif pnumfield == GribTypes.perturbationNumber:
                    pnum = grb.perturbationNumber
                else:
                    raise Exception('error pnum field')

                curkey = str(seqnum) if pnum == 0 else str(pnum) + '_' + str(seqnum)
                if seq_and_p_num is None:
                    rst[curkey] = grb
                else:
                    if curkey in seq_and_p_num:
                        rst[curkey] = grb

            LogLib.logger.info('FixReadData read_gribdata_from_grib2_with_pygrib_single_file_seqnum over %s' % (str(params)))
            return rst
        except Exception as data:
            LogLib.logger.error('FixReadData read_gribdata_from_grib2_with_pygrib_single_file_seqnum except %s %s' % (str(params), str(data)))

            return None
        
    #读多个grib2文件，具有相同的seqnums，返回以seqnum为key，文件中grib为value的字典的列表
    def read_gribdata_from_grib2_with_pygrib_mul_file_seqnum(self, params):
        from_files = params[FixParamTypes.SFullPaths]
        seq_and_p_num = params[FixParamTypes.SeqAndPNum] if FixParamTypes.SeqAndPNum in params else None

        try:
            LogLib.logger.info('FixReadData read_gribdata_from_grib2_with_pygrib_mul_file_seqnum start %s' % (str(params)))
            
            rsts = []
            curparams = {}
            curparams[FixParamTypes.SeqAndPNum] = seq_and_p_num

            for from_file in from_files:
                curparams[FixParamTypes.SFullPath] = from_file
                rst = self.read_gribdata_from_grib2_with_pygrib_single_file_seqnum(curparams)

                if rst is None:
                    return None
                else:
                    rsts.append(rst)

            LogLib.logger.info('FixReadData read_gribdata_from_grib2_with_pygrib_mul_file_seqnum over %s' % (str(params)))

            return rsts
        except Exception as data:
            LogLib.logger.error('FixReadData read_gribdata_from_grib2_with_pygrib_mul_file_seqnum except %s %s' % (str(params), str(data)))

            return None
        
    def read_std_from_diamond1(self, params):
        import meteva.base as meb

        from_file = params[FixParamTypes.SFullPath]
        
        try:
            LogLib.logger.info('FixReadData read_std_from_diamond1 start %s' % (str(params)))

            spd = meb.read_stadata_from_micaps1_2_8(from_file, meb.m1_element_column_dict["风速"]) 
            direction = meb.read_stadata_from_micaps1_2_8(from_file, meb.m1_element_column_dict["风向"]) #提取
            spd.rename(columns={'data0':'speed'}, inplace=True)
            spd['direction'] = direction.data0        #风速风向合并一个df

            return spd
        except Exception as data:
            LogLib.logger.error('FixReadData read_std_from_diamond1 except %s %s' % (str(params), str(data)))

            return None
        
    def read_stadata_from_meb_m3(self, params):
        import meteva.base as meb

        from_file = params[FixParamTypes.SFullPath]
        
        try:
            LogLib.logger.info('FixReadData read_stadata_from_meb_m3 start %s' % (str(params)))

            stadata = meb.read_stadata_from_micaps3(from_file)

            return stadata
        except Exception as data:
            LogLib.logger.error('FixReadData read_stadata_from_meb_m3 except %s %s' % (str(params), str(data)))

            return None

    def read_data_from_grads(self, params):
        from simplegrads import open_CtlDataset, CtlDescriptor, CtlVar

        from_file = params[FixParamTypes.SFullPath]
        dt = params[FixParamTypes.DT] if FixParamTypes.DT in params else None
        hase = params[FixParamTypes.HasE] if FixParamTypes.HasE in params else False
        encoding = params[FixParamTypes.Encoding] if FixParamTypes.Encoding in params else 'GBK'

        try:
            LogLib.logger.info('FixReadData read_data_from_grads start %s' % (str(params)))

            ds, ctl = open_CtlDataset(from_file, returnctl=True, encoding=encoding, hase=True, base_dt=dt)

            LogLib.logger.info('FixReadData read_data_from_grads over %s' % (str(params)))

            return (ds, ctl)
        except Exception as data:
            LogLib.logger.error('FixReadData read_data_from_grads except %s %s' % (str(params), str(data)))

            return None

    #读城镇报格式的预报数据，m3格式的实况
    def read_data_for_verify_province(self, params):
        from zczc import ZCZCParser
        import meteva.base as meb

        from_files = params[FixParamTypes.SFullPaths]
        staids = params[FixParamTypes.StaIDs] if FixParamTypes.StaIDs in params else None
        columns = params[FixParamTypes.Columns] if FixParamTypes.Columns in params else None
        filters = params[FixParamTypes.Filters] if FixParamTypes.Filters in params else None
        sname = params[FixParamTypes.SName] if FixParamTypes.SName in params else None

        try:
            LogLib.logger.info('FixReadData read_data_for_verify_province start %s' % (str(params)))
            zczcfile = from_files[0]
            zp = ZCZCParser()
            if not zp.parsefile(zczcfile, staids=staids, columns=columns, filters=filters):
                return None

            obsfiles = from_files[1]
            obsdatas = []
            for obsfile in obsfiles:
                obsdata = None
                if sname is None:
                    obsdata = meb.read_stadata_from_micaps3(obsfile)
                else:
                    obsdata = meb.read_stadata_from_micaps3(obsfile, data_name=sname)

                if obsdata is None:
                    LogLib.logger.error('FixReadData read_data_for_verify_province read obs error  %s' % (obsfile))

                else:
                    if staids is not None:
                        obsdata = obsdata[obsdata['id'].isin(staids)]

                obsdatas.append(obsdata)
            
            return [zp, obsdatas]
        except Exception as data:
            LogLib.logger.error('FixReadData read_data_for_verify_province except %s %s' % (str(params), str(data)))

            return None

if __name__ == '__main__':
    print('done')
