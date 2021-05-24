#!/usr/bin/python
# -*- coding: utf-8 -*-
#Filename: fixfileinfos.py

"""
Created on Aug 21, 2020

@author: anduin
"""

import datetime
import os
import re

from publictype.fixparamtypes import FixParamTypes
import public

class FixFileInfos(object):
    def __init__(self, logger, minsize=0):
        self.logger = logger
        self.minsize = minsize
        return super().__init__()
    
    '''
    def get_last_filename(self, dt, fix_dict, fix_fn_fmt, fix_seq, fix_fhs, fdelta):
        dt = dt.replace(minute=0)

        for i in range(2):
            while(True):
                if dt.hour in fix_fhs:
                    break
                else:
                    dt -= datetime.timedelta(hours=1)

            path = dt.strftime(fix_dict)
            tmpfnfmt = dt.strftime(fix_fn_fmt)
            
            ftime_last = None
            fullpath_last = None

            list_file = os.listdir(path)
            for fname in list_file:
                rersts = re.findall(tmpfnfmt, fname)
                if len(rersts) != 1:
                    continue

                ftime = datetime.datetime.strptime(rersts[0],  r'%Y%m%d%H%M%S')
                if fdelta is not None and (ftime >= dt + datetime.timedelta(minutes=fdelta) or ftime <= dt - datetime.timedelta(minutes=fdelta)):
                    continue

                if ftime_last is None or ftime_last < ftime:
                    ftime_last = ftime
                    fullpath_last = os.path.join(path, fname)

            if ftime_last is None:
                dt -= datetime.timedelta(hours=1)
            else:
                return (dt, fullpath_last)

        return (None, None)
    '''
    '''
    #dt是已经确定了起报时的时间
    def get_last_filename(self, dt, fix_dict, fix_fn_fmt, fix_seq, fix_fhs):
        dt = dt.replace(minute=0)
        
        while(True):
            if dt.hour in fix_fhs:
                break
            else:
                dt -= datetime.timedelta(hours=1)

        path = public.get_path_with_replace(fix_dict, dt=dt)
        tmpfnfmt = public.get_path_with_replace(fix_fn_fmt, dt=dt, seq=fix_seq)

        needre = False
        if tmpfnfmt.find('*') >= 0:
            tmpfnfmt = tmpfnfmt.replace('*', r'[\s\S]*?')
            needre = True
        
        fullpaths = []

        list_file = os.listdir(path)
        for fname in list_file:
            if needre:
                rersts = re.findall(tmpfnfmt, fname)
                if len(rersts) != 1:
                    continue
                
                fullpaths.append(fname)
            else:
                if fname == tmpfnfmt:
                    fullpaths.append(fname)

        if len(fullpaths) > 0:
            fullpaths.sort()

            return (dt, fullpaths[-1])
        else:
            return (dt, None)
        '''
    '''
    def get_save_filename(self, dt, save_dict, save_fn_fmt, save_seq, save_seq_fmt, save_fhs, fhsdelta):
        tmpdt = dt
        tmpdt += datetime.timedelta(minutes=fhsdelta)
        dt = dt.replace(minute=0)

        while(True):
            if tmpdt.hour in save_fhs:
                break
            else:
                tmpdt -= datetime.timedelta(hours=1)

        tmpdt = tmpdt.replace(minute=0)

        path = tmpdt.strftime(save_dict)
        tmpfnfmt = tmpdt.strftime(save_fn_fmt)
        
        fullpathinfos = {}
        for seq in save_seq:
            seqdt = tmpdt + datetime.timedelta(hours=seq)
            if dt < seqdt:
                fullpath = os.path.join(path, tmpfnfmt.replace(save_seq_fmt[0], save_seq_fmt[1] % seq))
                fullpathinfos[seq] = fullpath

        return (tmpdt, fullpathinfos)
    '''

    #多个源文件路径，找各自的最后一个文件
    #根据dt和格式确定源路径，判断路径是否存在。
    def get_fix_path_list_last(self, params):
        dt = params[FixParamTypes.DT]
        fix_dict = params[FixParamTypes.SDict]
        fix_fn_fmt = params[FixParamTypes.SFnFmt]
        fix_seq = params[FixParamTypes.SSeq] if FixParamTypes.SSeq in params else None
        s_f_delta = params[FixParamTypes.SFDelta] if FixParamTypes.SFDelta in params else None

        try:
            self.logger.info('FixFileInfos get_fix_path_list_last start %s' % (str(params)))
            path = public.get_path_with_replace(fix_dict, dt=dt)
            if not os.path.exists(path):
                self.logger.warning('FixFileInfos get_fix_path_list_last no file')
                return None

            tmpfnfmt = public.get_path_with_replace(fix_fn_fmt, dt=dt, seq=fix_seq)

            needre = False
            if tmpfnfmt.find('*') >= 0:
                tmpfnfmt = tmpfnfmt.replace('*', r'([\s\S]*?)')
                needre = True
        
            fullpaths = []

            list_file = os.listdir(path)
            for fname in list_file:
                if needre:
                    rersts = re.findall(tmpfnfmt, fname)
                    if len(rersts) != 1:
                        continue

                    if s_f_delta is not None:
                        dt_file = datetime.datetime.strptime(rersts[0], '%Y%m%d%H%M%S')
                        if dt_file < dt + datetime.timedelta(minutes=s_f_delta[0]) or dt_file > dt + datetime.timedelta(minutes=s_f_delta[1]):
                            continue

                    fullpaths.append(fname)
                else:
                    if fname == tmpfnfmt:
                        fullpaths.append(fname)

            if len(fullpaths) > 0:
                fullpaths.sort()

                self.logger.info('FixFileInfos get_fix_path_list_last over')
                return os.path.join(path, fullpaths[-1])
            else:
                self.logger.warning('FixFileInfos get_fix_path_list_last no file')
                return None
        except Exception as data:
            self.logger.error('FixFileInfos get_fix_path_list_last except %s %s' % (str(params), str(data)))

            raise data
            
    #多个源文件路径，找各自的最后一个文件
    #根据dt和格式确定源路径，判断路径是否存在。
    def get_save_path(self, params):
        dt = params[FixParamTypes.DT]
        save_dict = params[FixParamTypes.DDict]
        save_fn_fmt = params[FixParamTypes.DFnFmt]
        save_seq = params[FixParamTypes.DSeq]
        
        logger = params[FixParamTypes.CurLogger] if FixParamTypes.CurLogger in params else None
        if logger is None:
            logger = self.logger

        try:
            self.logger.info('FixFileInfos get_save_path start %s' % (str(params)))
            saveinfos = {}
            
            path = public.get_path_with_replace(save_dict, dt=dt)
            for s in save_seq:
                tmpfnfmt = public.get_path_with_replace(save_fn_fmt, dt=dt, seq=s)

                saveinfos[s] = os.path.join(path, tmpfnfmt)

            self.logger.info('FixFileInfos get_save_path over')

            return saveinfos
        except Exception as data:
            self.logger.error('FixFileInfos get_save_path except %s %s' % (str(params), str(data)))

            raise data
            
if __name__ == '__main__':
    print('done')
