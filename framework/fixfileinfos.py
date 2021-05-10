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
import copy
import time

from logmodule.loglib import *
from publictype.fixparamtypes import FixParamTypes

class FixFileInfos(object):
    def __init__(self, minsize=0):
        self.minsize = minsize
        return super().__init__()
    
    #名字相同，根据fix_fn_fmt过滤掉部分文件
    def filter_fn_samefn(self, fname, fix_fn_fmt, save_fn_fmt, delta=None, sdt=None, seqobj=None):
        rsts = re.findall(fix_fn_fmt, fname)
        if len(rsts) != 1:
            return (None, None)
        else:
            return (fname, None)

    #名字相同，可以更换扩展名
    def change_fn_samefn(self, fname, fix_fn_fmt, save_fn_fmt, delta=None, sdt=None, seqobj=None):
        sname = fname
        if fix_fn_fmt is not None and save_fn_fmt is not None:
            if len(fix_fn_fmt) == 0:
                sname += save_fn_fmt
            else:
                if sname[-len(fix_fn_fmt):] == fix_fn_fmt:
                    sname = sname[:-len(fix_fn_fmt)] + save_fn_fmt
                else:
                    raise Exception('fix_fn_fmt error %s' % (fix_fn_fmt))

        return (sname, None)

    #提取部分源文件名，替换到目标文件名，允许多个部分拼接
    def change_fn_subfn(self, fname, fix_fn_fmt, save_fn_fmt, delta=None, sdt=None, seqobj=None):
        sname = fname
        rsts = re.findall(fix_fn_fmt, fname)
        if len(rsts) == 1:
            sname = save_fn_fmt % rsts[0]
        else:
            raise Exception('fix_fn_fmt error %s' % (fix_fn_fmt))

        return (sname, None)
    
    #提取是时间的部分源文件名，替换到目标文件名，考虑时间转换，提取的部分拼接到一起，为%Y%m%d%H%M，长度不够补0，
    def change_fn_subfn_tz(self, fname, fix_fn_fmt, save_fn_fmt, delta=None, sdt=None, seqobj=None):
        sname = fname
        rsts = re.findall(fix_fn_fmt, fname)
        if len(rsts) == 1:
            tstr = ''.join(rsts[0])
            tstr_len = len(tstr)
            if tstr_len < 8 or tstr_len % 2 == 1:
                raise Exception('fix_fn_fmt or file name error %s %s' % (fix_fn_fmt, fname))
            
            cplen = min(12, tstr_len)
            tmpstr = '000000000000'
            tstr = tstr[:cplen] + tmpstr[cplen:12]
            dt = datetime.datetime.strptime(tstr, '%Y%m%d%H%M')
            if delta is not None:
                dt += datetime.timedelta(hours = delta)

            sname = dt.strftime(save_fn_fmt)
        else:
            raise Exception('fix_fn_fmt or file name error %s %s' % (fix_fn_fmt, fname))

        return (sname, dt)
    
    def change_fn_subfn_tz_and_seq(self, fname, fix_fn_fmt, save_fn_fmt, delta=None, sdt=None, seqobj=None):
        sname = fname

        patt = dt.strftime(fix_fn_fmt)
        rsts = re.findall(patt, fname)
        if len(rsts) != 1:
            raise Exception('fix_fn_fmt or file name error %s %s' % (fix_fn_fmt, fname))
        
        if int(rsts[0]) not in seqobj:
            return None

        #2019123000.001.nc
        cur_save_fn_fmt = save_fn_fmt.replace('FFF', '%03d' % int(rsts[0]))
        savedt = dt
        if delta != 0:
            savedt = dt + datetime.timedelta(hours=delta)

        sname = savedt.strftime(save_fn_fmt)

        return (sname, dt)
    
    #针对处理目录中所有文件，文件名处理有函数完成。
    #目标文件不存在，将文件名和目标文件名存入列表。
    def get_fix_file_list_with_dt_procfn(self, params):
        dt = params[FixParamTypes.DT]
        fix_dict = params[FixParamTypes.SDict]
        save_dict = params[FixParamTypes.DDict]
        fix_fn_fmt = params[FixParamTypes.SFnFmt] if FixParamTypes.SFnFmt in params else None
        save_fn_fmt = params[FixParamTypes.DFnFmt] if FixParamTypes.DFnFmt in params else None
        proc = params[FixParamTypes.Proc] if FixParamTypes.Proc in params else None
        delta = params[FixParamTypes.TZ_Delta] if FixParamTypes.TZ_Delta in params else None
        seqobj = params[FixParamTypes.SeqObj] if FixParamTypes.SeqObj in params else None

        try:
            LogLib.logger.info('FixFileInfos get_fix_file_list_with_dt_procfn start %s' % (dt.strftime('%Y-%m-%d %H:%M:%S')))
            path = dt.strftime(fix_dict)
            if not os.path.exists(path):
                LogLib.logger.info('FixFileInfos get_fix_file_list_with_dt_procfn path not exist:%s' % (path))
                return {}

            if not os.path.isdir(path):
                LogLib.logger.error('FixFileInfos get_fix_file_list_with_dt_procfn path is not dir:%s' % (path))
                return {}

            fixfullpaths = {}
        
            list_file = os.listdir(path)
            for fname in list_file:
                fullpath = os.path.join(path, fname)

                if not os.path.isfile(fullpath):
                    LogLib.logger.error('FixFileInfos get_fix_file_list_with_dt_procfn fullpath is not file:%s' % (fullpath))
                    continue

                if self.minsize > 0 and os.path.getsize(fullpath) <= self.minsize:
                    LogLib.logger.info('FixFileInfos get_fix_file_list_with_dt_procfn fullpath is empty:%s' % (fullpath))
                    continue

                sname = fname
                sdt = dt
                if proc is not None:
                    rst = proc(fname, fix_fn_fmt, save_fn_fmt, delta, sdt=dt, seqobj=seqobj)
                    if rst is None or rst[0] is None:
                        continue

                    sname = rst[0]
                    if rst[1] is not None:
                        sdt = rst[1]

                savefullpath = os.path.join(sdt.strftime(save_dict), sname)
                if not os.path.exists(savefullpath):
                    fixfullpaths[fullpath] = savefullpath
                else:
                    LogLib.logger.info('FixFileInfos get_fix_file_list_with_dt_procfn exist %s' % (savefullpath))

            LogLib.logger.info('FixFileInfos get_fix_file_list_with_dt_procfn over')

            return fixfullpaths
        except Exception as data:
            LogLib.logger.error('FixFileInfos get_fix_file_list_with_dt_procfn except %s %s' % (dt.strftime('%Y-%m-%d %H:%M:%S'), str(data)))

            raise data
    '''
    #针对处理目录中所有文件，并且文件名不变的情况，扩展名可变，也可不变。
    #目标文件不存在，将文件名和目标文件名存入列表。
    def get_fix_file_list_with_dt_samefn(self, params):
        dt = params[FixParamTypes.DT]
        fix_dict = params[FixParamTypes.SDict]
        save_dict = params[FixParamTypes.DDict]
        fix_fn_fmt = params[FixParamTypes.SFnFmt] if FixParamTypes.SFnFmt in params else None
        save_fn_fmt = params[FixParamTypes.DFnFmt] if FixParamTypes.DFnFmt in params else None

        try:
            LogLib.logger.info('FixFileInfos get_fix_file_list_with_dt_samefn start %s' % (dt.strftime('%Y-%m-%d %H:%M:%S')))
            path = dt.strftime(fix_dict)
            if not os.path.exists(path):
                LogLib.logger.info('FixFileInfos get_fix_file_list_with_dt_samefn path not exist:%s' % (path))
                return {}

            if not os.path.isdir(path):
                LogLib.logger.error('FixFileInfos get_fix_file_list_with_dt_samefn path is not dir:%s' % (path))
                return {}

            fixfullpaths = {}
        
            list_file = os.listdir(path)
            for fname in list_file:
                fullpath = os.path.join(path, fname)

                if not os.path.isfile(fullpath):
                    LogLib.logger.error('FixFileInfos get_fix_file_list_with_dt_samefn fullpath is not file:%s' % (fullpath))
                    continue

                if self.minsize > 0 and os.path.getsize(fullpath) <= self.minsize:
                    LogLib.logger.info('FixFileInfos get_fix_file_list_with_dt_samefn fullpath is empty:%s' % (fullpath))
                    continue

                sname = fname
                if fix_fn_fmt is not None and save_fn_fmt is not None:
                    if len(fix_fn_fmt) == 0:
                        sname += save_fn_fmt
                    else:
                        if sname[-len(fix_fn_fmt):] == fix_fn_fmt:
                            sname = sname[:-len(fix_fn_fmt)] + save_fn_fmt
                        else:
                            raise Exception('fix_fn_fmt error %s' % (fix_fn_fmt))

                savefullpath = os.path.join(dt.strftime(save_dict), sname)
                if not os.path.exists(savefullpath):
                    fixfullpaths[fullpath] = savefullpath
                else:
                    LogLib.logger.info('FixFileInfos get_fix_file_list_with_dt_samefn exist %s' % (savefullpath))

            LogLib.logger.info('FixFileInfos get_fix_file_list_with_dt_samefn over')

            return fixfullpaths
        except Exception as data:
            LogLib.logger.error('FixFileInfos get_fix_file_list_with_dt_samefn except %s %s' % (dt.strftime('%Y-%m-%d %H:%M:%S'), str(data)))

            raise data
            '''

    '''
    #使用get_fix_file_list_with_dt_procfn代替
    #针对目录文件比较少的情况，多为以小时为目录名
    #根据dt确定目录，列举目录中的文件，判断文件是否符合格式，如果符合，确定该文件对应的目标文件是否存在。
    #目标文件不存在，将文件名和目标文件名存入列表。
    def get_fix_file_list_with_dt(self, params):
        dt = params[FixParamTypes.DT]
        fix_dict = params[FixParamTypes.SDict]
        fix_fn_fmt = params[FixParamTypes.SFnFmt]
        save_dict = params[FixParamTypes.DDict]
        save_fn_fmt = params[FixParamTypes.DFnFmt]
        seqobj = params[FixParamTypes.SeqObj]
        delta = params[FixParamTypes.TZ_Delta]

        try:
            LogLib.logger.info('FixFileInfos get_fix_file_list_with_dt start %s' % (dt.strftime('%Y-%m-%d %H:%M:%S')))
            path = dt.strftime(fix_dict)
            if not os.path.exists(path):
                LogLib.logger.info('FixFileInfos get_fix_file_list_with_dt path not exist:%s' % (path))
                return {}

            if not os.path.isdir(path):
                LogLib.logger.error('FixFileInfos get_fix_file_list_with_dt path is not dir:%s' % (path))
                return {}

            patt = dt.strftime(fix_fn_fmt)

            fixfullpaths = {}
        
            list_file = os.listdir(path)
            for fname in list_file:
                fullpath = os.path.join(path, fname)

                if not os.path.isfile(fullpath):
                    LogLib.logger.error('FixFileInfos get_fix_file_list_with_dt fullpath is not file:%s' % (fullpath))
                    continue

                if self.minsize > 0 and os.path.getsize(fullpath) <= self.minsize:
                    LogLib.logger.info('FixFileInfos get_fix_file_list_with_dt fullpath is empty:%s' % (fullpath))
                    continue

                rsts = re.findall(patt, fname)
                if len(rsts) != 1:
                    continue
        
                if int(rsts[0]) not in seqobj:
                    continue

                #2019123000.001.nc
                cur_save_fn_fmt = save_fn_fmt.replace('FFF', '%03d' % int(rsts[0]))
                savedt = dt
                if delta != 0:
                    savedt = dt + datetime.timedelta(hours=delta)

                savefullpath = os.path.join(savedt.strftime(save_dict), savedt.strftime(cur_save_fn_fmt))
                if not os.path.exists(savefullpath):
                    fixfullpaths[fullpath] = savefullpath
                else:
                    LogLib.logger.info('FixFileInfos get_fix_file_list_with_dt exist %s' % (savefullpath))

            LogLib.logger.info('FixFileInfos get_fix_file_list_with_dt over')

            return fixfullpaths
        except Exception as data:
            LogLib.logger.error('FixFileInfos get_fix_file_list_with_dt except %s %s' % (dt.strftime('%Y-%m-%d %H:%M:%S'), str(data)))

            raise data
            '''
    #dt_fmt是针对文件名，[['xxx','%Y%m%d%H'],['yyy', '%Y%m%d%H']],可以没有,最多为2个，后一个时间为dt加seqnum，seqnum必须为预报时序，并且有值
    def fillFileName(self, dt, fn_fmt, seqnum, seq_fmt, dt_fmt):
        fname = fn_fmt
        if seqnum is not None:
            fname = fn_fmt.replace(seq_fmt[0], seq_fmt[1] % (seqnum))

        if dt_fmt is not None and len(dt_fmt) > 0:
            fname = fname.replace(dt_fmt[0][0], dt.strftime(dt_fmt[0][1]))
            if len(dt_fmt) > 1:
                if type(seqnum) is not int:
                    raise Exception('dt_fmt多个数据时，seqnum必须是int。')

                fname = fname.replace(dt_fmt[1][0], (dt+ datetime.timedelta(hours=seqnum)).strftime(dt_fmt[1][1]))

        return fname

    #dt_fmt是针对文件名，[['xxx','%Y%m%d%H'],['yyy', '%Y%m%d%H']],可以没有,最多为2个，后一个时间为dt加seqnum，seqnum必须为预报时序，并且有值
    def getFixFullPath(self, dt, fix_path, fix_fn_fmt, seqnum=None, seq_fmt=['FFF', '%03d'], dt_fmt=None, is_exist=True, is_url=False):
        fname = self.fillFileName(dt, fix_fn_fmt, seqnum, seq_fmt, dt_fmt)

        fullpath = ''
        if is_url:
            from urllib.parse import urljoin
            fullpath = urljoin(fix_path, fname)
        else:
            fullpath = os.path.join(fix_path, fname)

        if not is_exist:
            return (True, fullpath, fname)

        if not os.path.exists(fullpath):
            LogLib.logger.info('FixFileInfos getFixFullPath fullpath not exist:%s' % (fullpath))
            return (False, fullpath, fname)
                    
        if not os.path.isfile(fullpath):
            LogLib.logger.error('FixFileInfos getFixFullPath fullpath is not file:%s' % (fullpath))
            return (False, fullpath, fname)
                    
        if self.minsize > 0 and os.path.getsize(fullpath) <= self.minsize:
            LogLib.logger.info('FixFileInfos getFixFullPath fullpath is empty:%s' % (fullpath))
            return (False, fullpath, fname)

        return (True, fullpath, fname)
    
    def getFixFullPathForGDS(self, dt, path, fix_fn_fmt, seqnum=None, seq_fmt=['FFF', '%03d'], dt_fmt=None):
        fname = self.fillFileName(dt, fix_fn_fmt, seqnum, seq_fmt, dt_fmt)

        fullpath = path + r'/' + fname

        return (True, fullpath, fname)
    
    #dt_fmt是针对文件名，[['xxx','%Y%m%d%H'],['yyy', '%Y%m%d%H']],可以没有，最多为2个，后一个时间为dt加seqnum，seqnum必须为预报时序，并且有值
    def getSaveFullPath(self, dt, save_dict, save_fn_fmt, delta=0, seqnum=None, seq_fmt=['FFF', '%03d'], dt_fmt=None, is_exist=True, f_delta=None):
        savedt = dt
        if delta != 0:
            savedt = dt + datetime.timedelta(hours=delta)

        fname = self.fillFileName(savedt, save_fn_fmt, seqnum, seq_fmt, dt_fmt)

        save_path = savedt.strftime(save_dict)
        savefullpath = os.path.join(save_path, fname)

        if not os.path.exists(save_path):
            #os.makedirs(save_path)
            return (True, savefullpath)

        if os.path.exists(savefullpath):
            if not is_exist:
                return (True, savefullpath)
            
            if f_delta is None:
                return (False, savefullpath)
            else:
                if ((dt + datetime.timedelta(minutes=f_delta)) < datetime.datetime.fromtimestamp(os.path.getmtime(savefullpath))):
                    return (False, savefullpath)
                else:
                    return (True, savefullpath)
        else:
            return (True, savefullpath)

    #针对目录中文件很多的情况，多为以天为目录名
    #根据dt和格式确定文件名，判断文件是否存在，如果存在，确定该文件对应的目标文件是否存在。
    #目标文件不存在，将文件名和目标文件名存入列表。
    def get_fix_file_list_with_path(self, params):
        dt = params[FixParamTypes.DT]
        fix_dict = params[FixParamTypes.SDict]
        fix_fn_fmt = params[FixParamTypes.SFnFmt]
        save_dict = params[FixParamTypes.DDict]
        save_fn_fmt = params[FixParamTypes.DFnFmt]
        seqobj = params[FixParamTypes.SeqObj] if FixParamTypes.SeqObj in params else [None]
        if len(seqobj) == 0:
            seqobj = [None]

        #预报时效在文件名中的格式，第一个值是源文件的，第二个是目标文件的
        seqfmt = params[FixParamTypes.SeqFmt] if FixParamTypes.SeqFmt in params else [None, None]  #[['FFF', '%03d'], ['FFF', '%03d']]
        delta = params[FixParamTypes.TZ_Delta] if FixParamTypes.TZ_Delta in params else 0
        spathexist = params[FixParamTypes.SPathExist] if FixParamTypes.SPathExist in params else True
        dpathexist = params[FixParamTypes.DPathExist] if FixParamTypes.DPathExist in params else True
        #时间在文件名中的格式，第一个值是源文件的，第二个是目标文件的。
        dt_fmt = params[FixParamTypes.DTFmt] if FixParamTypes.DTFmt in params else [None, None]
        is_url = params[FixParamTypes.IsUrl] if FixParamTypes.IsUrl in params else False

        try:
            LogLib.logger.info('FixFileInfos get_fix_file_list_with_path start %s' % (dt.strftime('%Y-%m-%d %H:%M:%S')))
            path = dt.strftime(fix_dict)
            if spathexist:
                if not os.path.exists(path):
                    LogLib.logger.info('FixFileInfos get_fix_file_list_with_path path not exist:%s' % (path))
                    return {}

                if not os.path.isdir(path):
                    LogLib.logger.error('FixFileInfos get_fix_file_list_with_path path is not dir:%s' % (path))
                    return {}

            fixfullpaths = {}
        
            for i in seqobj:
                rst, fullpath, fixname = self.getFixFullPath(dt, path, fix_fn_fmt, seqnum=i, seq_fmt=seqfmt[0], dt_fmt=dt_fmt[0], is_exist=spathexist, is_url=is_url)
                if not rst:
                    continue

                rst, savefullpath = self.getSaveFullPath(dt, save_dict, save_fn_fmt, delta=delta, seqnum=i, seq_fmt=seqfmt[1], dt_fmt=dt_fmt[1], is_exist=dpathexist)
                if rst:
                    fixfullpaths[fullpath] = [savefullpath, i, dt+datetime.timedelta(hours=delta)]
                else:
                    LogLib.logger.info('FixFileInfos get_fix_file_list_with_path exist %s' % (savefullpath))

            LogLib.logger.info('FixFileInfos get_fix_file_list_with_path over')

            return fixfullpaths
        except Exception as data:
            LogLib.logger.error('FixFileInfos get_fix_file_list_with_path except %s %s' % (dt.strftime('%Y-%m-%d %H:%M:%S'), str(data)))

            raise data
            
    #针对目录中文件很多的情况，多为以天为目录名
    #根据dt和格式确定文件名，判断文件是否存在，如果存在，确定该文件对应的目标文件是否存在。
    #目标文件不存在，将文件名和目标文件名存入列表。
    #目标文件有多个，seqobj是针对目标文件的。
    def get_fix_file_list_with_path_ctl(self, params):
        from simplegrads import CtlDescriptor

        dt = params[FixParamTypes.DT]
        fix_dict = params[FixParamTypes.SDict]
        fix_fn_fmt = params[FixParamTypes.SFnFmt]
        save_dict = params[FixParamTypes.DDict]
        save_fn_fmt = params[FixParamTypes.DFnFmt]

        #预报时效在文件名中的格式，第一个值是源文件的，第二个是目标文件的
        seqfmt = params[FixParamTypes.SeqFmt]
        delta = params[FixParamTypes.TZ_Delta] if FixParamTypes.TZ_Delta in params else 0
        spathexist = params[FixParamTypes.SPathExist] if FixParamTypes.SPathExist in params else True
        dpathexist = params[FixParamTypes.DPathExist] if FixParamTypes.DPathExist in params else True
        #时间在文件名中的格式，第一个值是源文件的，第二个是目标文件的。
        dt_fmt = params[FixParamTypes.DTFmt] if FixParamTypes.DTFmt in params else [None, None]
        is_url = params[FixParamTypes.IsUrl] if FixParamTypes.IsUrl in params else False
        hase = params[FixParamTypes.HasE] if FixParamTypes.HasE in params else False
        encoding = params[FixParamTypes.Encoding] if FixParamTypes.Encoding in params else 'GBK'

        try:
            LogLib.logger.info('FixFileInfos get_fix_file_list_with_path_ctl start %s' % (dt.strftime('%Y-%m-%d %H:%M:%S')))
            path = dt.strftime(fix_dict)
            if spathexist:
                if not os.path.exists(path):
                    LogLib.logger.info('FixFileInfos get_fix_file_list_with_path_ctl path not exist:%s' % (path))
                    return {}

                if not os.path.isdir(path):
                    LogLib.logger.error('FixFileInfos get_fix_file_list_with_path_ctl path is not dir:%s' % (path))
                    return {}

            fixfullpaths = {}
        
            rst, fullpath, fixname = self.getFixFullPath(dt, path, fix_fn_fmt, seqnum=None, seq_fmt=seqfmt[0], dt_fmt=dt_fmt[0], is_exist=spathexist, is_url=is_url)
            if not rst:
                return {}

            ctl = CtlDescriptor(encoding=encoding, file=fullpath, hase=hase, base_dt=dt)
            if not ctl.hasData:
                return {}

            for i in ctl.seq: # seqobj:
                rst, savefullpath = self.getSaveFullPath(dt, save_dict, save_fn_fmt, delta=delta, seqnum=i, seq_fmt=seqfmt[1], dt_fmt=dt_fmt[1], is_exist=dpathexist)
                if rst:
                    if ctl in fixfullpaths:
                        fixfullpaths[ctl].append([savefullpath, i, dt+datetime.timedelta(hours=delta)])
                    else:
                        fixfullpaths[ctl] = [[savefullpath, i, dt+datetime.timedelta(hours=delta)]]
                else:
                    LogLib.logger.info('FixFileInfos get_fix_file_list_with_path_ctl exist %s' % (savefullpath))

            LogLib.logger.info('FixFileInfos get_fix_file_list_with_path_ctl over')

            return fixfullpaths
        except Exception as data:
            LogLib.logger.error('FixFileInfos get_fix_file_list_with_path_ctl except %s %s' % (dt.strftime('%Y-%m-%d %H:%M:%S'), str(data)))

            raise data
            
    #针对累加的情况获取文件信息
    #根据dt和格式确定文件名，判断文件是否存在，如果不存在，返回空数据。
    #文件存在，将文件名存入列表。然后判断目标文件是否存在，存在，返回空数据，不存在，返回目标文件名和文件列表。
    def get_check_file_list_with_path(self, params):
        dt = params[FixParamTypes.DT]
        fix_dict = params[FixParamTypes.SDict]
        fix_fn_fmt = params[FixParamTypes.SFnFmt]
        save_dict = params[FixParamTypes.DDict]
        save_fn_fmt = params[FixParamTypes.DFnFmt]
        seqobj = params[FixParamTypes.SeqObj] if FixParamTypes.SeqObj in params else [None]
        if len(seqobj) == 0:
            seqobj = [None]

        #预报时效在文件名中的格式，第一个值是源文件的，第二个是目标文件的
        seqfmt = params[FixParamTypes.SeqFmt] if FixParamTypes.SeqFmt in params else [None, None]  #[['FFF', '%03d'], ['FFF', '%03d']]
        delta = params[FixParamTypes.TZ_Delta] if FixParamTypes.TZ_Delta in params else 0
        spathexist = params[FixParamTypes.SPathExist] if FixParamTypes.SPathExist in params else True
        dpathexist = params[FixParamTypes.DPathExist] if FixParamTypes.DPathExist in params else True
        #时间在文件名中的格式，第一个值是源文件的，第二个是目标文件的。
        dt_fmt = params[FixParamTypes.DTFmt] if FixParamTypes.DTFmt in params else [None, None]
        is_url = params[FixParamTypes.IsUrl] if FixParamTypes.IsUrl in params else False

        dts = params[FixParamTypes.DTS] if FixParamTypes.DTS in params else None
        deltas = params[FixParamTypes.Deltas] if FixParamTypes.Deltas in params else None

        try:
            LogLib.logger.info('FixFileInfos get_check_file_list_with_path start %s' % (dt.strftime('%Y-%m-%d %H:%M:%S')))

            fixfullpaths = []
            
            if dts is None:
                if deltas is not None:
                    dts = copy.deepcopy(deltas)
                
                    def y3(x):
                        return dt + datetime.timedelta(minutes=x)

                    dts = list(map(y3, dts))
                else:
                    dts = [dt]

            for curdt in dts:
                path = curdt.strftime(fix_dict)
                if spathexist:
                    if not os.path.exists(path):
                        LogLib.logger.info('FixFileInfos get_check_file_list_with_path path not exist:%s' % (path))
                        return ('', [])

                    if not os.path.isdir(path):
                        LogLib.logger.error('FixFileInfos get_check_file_list_with_path path is not dir:%s' % (path))
                        return ('', [])

                for i in seqobj:
                    rst, fullpath, fixname = self.getFixFullPath(curdt, path, fix_fn_fmt, seqnum=i, seq_fmt=seqfmt[0], dt_fmt=dt_fmt[0], is_exist=spathexist, is_url=is_url)
                    if not rst:
                        return ('', [])

                    fixfullpaths.append([fullpath, i])

            if len(fixfullpaths) == 0:
                LogLib.logger.info('FixFileInfos get_check_file_list_with_path over no file')
                return ('', [])

            rst, savefullpath = self.getSaveFullPath(dt, save_dict, save_fn_fmt, delta=delta, dt_fmt=dt_fmt[1], is_exist=dpathexist)
            if rst:
                LogLib.logger.info('FixFileInfos get_check_file_list_with_path over')
                return (savefullpath, fixfullpaths)
            else:
                LogLib.logger.info('FixFileInfos get_check_file_list_with_path exist %s' % (savefullpath))
                return ('', [])
        except Exception as data:
            LogLib.logger.error('FixFileInfos get_check_file_list_with_path except %s %s' % (dt.strftime('%Y-%m-%d %H:%M:%S'), str(data)))

            raise data
            
    def seq_minute_to_hour(self, seqnum):
        return seqnum / 60

    #针对Cassandra，源是压缩文件，压缩文件只有一个文件
    #根据dt和格式确定压缩文件名，不判断文件是否存在，确定该文件对应的目标文件是否存在。
    #目标文件不存在，将文件名和目标文件名存入列表。
    def get_fix_file_list_with_path_compress_onlyone(self, params):
        from meteva.base.io.GDS_data_service import GDSDataService
        from meteva.base.io import DataBlock_pb2

        dts = params[FixParamTypes.DTS]
        fix_dict = params[FixParamTypes.SDict]
        fix_fn_fmt = params[FixParamTypes.SFnFmt]
        save_dict = params[FixParamTypes.DDict]
        save_fn_fmt = params[FixParamTypes.DFnFmt]
        seqobj = params[FixParamTypes.SeqObj] if FixParamTypes.SeqObj in params else [None]
        if len(seqobj) == 0:
            seqobj = [None]

        seq_proc = params[FixParamTypes.SeqProc] if FixParamTypes.SeqProc in params else None
        gds_id = params[FixParamTypes.SrvIP]
        gds_port = params[FixParamTypes.SrvPort]

        #预报时效在文件名中的格式，第一个值是源文件的，第二个是目标文件的
        seqfmt = params[FixParamTypes.SeqFmt] if FixParamTypes.SeqFmt in params else [None, None]  #[['FFF', '%03d'], ['FFF', '%03d']]
        delta = params[FixParamTypes.TZ_Delta] if FixParamTypes.TZ_Delta in params else 0
        spathexist = params[FixParamTypes.SPathExist] if FixParamTypes.SPathExist in params else True
        dpathexist = params[FixParamTypes.DPathExist] if FixParamTypes.DPathExist in params else True
        #时间在文件名中的格式，第一个值是源文件的，第二个是目标文件的。
        dt_fmt = params[FixParamTypes.DTFmt] if FixParamTypes.DTFmt in params else [None, None]

        try:
            LogLib.logger.info('FixFileInfos get_fix_file_list_with_path_compress_onlyone start %s' % (str(params)))
            path = fix_dict

            # connect to data service
            service = GDSDataService(gdsIp=gds_id, gdsPort=gds_port)
            
            # 获得指定目录下的所有文件
            status, response = service.getFileList(path)
            file_list = []
            if status != 200:
                LogLib.logger.error('FixFileInfos get_fix_file_list_with_path_compress_onlyone GDSDataService getFileList error %s' % (str(params)))
                return None
                
            mrst = DataBlock_pb2.MapResult()
            if mrst is None:
                LogLib.logger.error('FixFileInfos get_fix_file_list_with_path_compress_onlyone MappingResult error %s' % (str(params)))
                return None

            # Protobuf的解析
            mrst.ParseFromString(response)
            if mrst.errorCode != 0:
                LogLib.logger.error('FixReadData get_fix_file_list_with_path_compress_onlyone ByteArrayResult error %d %s %s' % (mrst.errorCode, mrst.errorMessage, str(params)))
                return None

            results = mrst.resultMap
            # 遍历指定目录
            for name_size_pair in results.items():
                if (name_size_pair[1] != 'D'):
                    file_list.append(name_size_pair[0])

            file_set = set(file_list)

            fixfullpaths = {}
        
            for dt in dts:
                for i in seqobj:
                    rst, fullpath, fname = self.getFixFullPathForGDS(dt, path, fix_fn_fmt, seqnum=i, seq_fmt=seqfmt[0], dt_fmt=dt_fmt[0])
                    if not rst:
                        continue

                    if fname not in file_set:
                        continue

                    saveseqnum = i
                    if seq_proc is not None:
                        saveseqnum = seq_proc(i)

                    rst, savefullpath = self.getSaveFullPath(dt, save_dict, save_fn_fmt, delta=delta, seqnum=saveseqnum, seq_fmt=seqfmt[1], dt_fmt=dt_fmt[1], is_exist=dpathexist)
                    if rst:
                        fixfullpaths[fullpath] = savefullpath
                    else:
                        LogLib.logger.info('FixFileInfos get_fix_file_list_with_path_compress_onlyone exist %s' % (savefullpath))

            LogLib.logger.info('FixFileInfos get_fix_file_list_with_path_compress_onlyone over')

            return fixfullpaths
        except Exception as data:
            LogLib.logger.error('FixFileInfos get_fix_file_list_with_path_compress_onlyone except %s %s' % (str(params), str(data)))

            raise data
            
    #针对Cassandra，下载所有文件
    def get_fix_file_list_with_path_cassandra_all(self, params):
        from meteva.base.io.GDS_data_service import GDSDataService
        from meteva.base.io import DataBlock_pb2

        fix_dict = params[FixParamTypes.SDict]
        fix_fn_fmt = params[FixParamTypes.SFnFmt]
        save_dict = params[FixParamTypes.DDict]
        gds_id = params[FixParamTypes.SrvIP]
        gds_port = params[FixParamTypes.SrvPort]
        dt_fmt = params[FixParamTypes.DTFmt]
        proc = params[FixParamTypes.Proc]
        dt0 = params[FixParamTypes.STime]
        fhs = params[FixParamTypes.FHS] if FixParamTypes.FHS in params else None

        try:
            LogLib.logger.info('FixFileInfos get_fix_file_list_with_path_cassandra_all start %s' % (str(params)))
            path = fix_dict

            # connect to data service
            service = GDSDataService(gdsIp=gds_id, gdsPort=gds_port)
            
            # 获得指定目录下的所有文件
            status, response = service.getFileList(path)
            file_list = []
            if status != 200:
                LogLib.logger.error('FixFileInfos get_fix_file_list_with_path_cassandra_all GDSDataService getFileList error %s' % (str(params)))
                return None
                
            mrst = DataBlock_pb2.MapResult()
            if mrst is None:
                LogLib.logger.error('FixFileInfos get_fix_file_list_with_path_cassandra_all MappingResult error %s' % (str(params)))
                return None

            # Protobuf的解析
            mrst.ParseFromString(response)
            if mrst.errorCode != 0:
                LogLib.logger.error('FixReadData get_fix_file_list_with_path_cassandra_all ByteArrayResult error %d %s %s' % (mrst.errorCode, mrst.errorMessage, str(params)))
                return None

            results = mrst.resultMap
            # 遍历指定目录
            for name_size_pair in results.items():
                if (name_size_pair[1] != 'D'):
                    file_list.append(name_size_pair[0])

            fixfullpaths = {}
            
            for fname in file_list:
                fullpath = path + '/' + fname

                dt = proc(fname, fix_fn_fmt, dt_fmt)
                if dt < dt0:
                    continue

                if fhs is not None:
                    if dt.hour not in fhs:
                        continue
    
                savefullpath = os.path.join(dt.strftime(save_dict), fname)
                if os.path.exists(savefullpath):
                    LogLib.logger.info('FixFileInfos get_fix_file_list_with_path_cassandra_all exist %s' % (savefullpath))
                else:
                    fixfullpaths[fullpath] = savefullpath

            LogLib.logger.info('FixFileInfos get_fix_file_list_with_path_cassandra_all over')

            return fixfullpaths
        except Exception as data:
            LogLib.logger.error('FixFileInfos get_fix_file_list_with_path_cassandra_all except %s %s' % (str(params), str(data)))

            raise data
            
    #通过接口直接获得数据，根据dt和格式确定目标文件名
    def get_fix_file_list_with_path_cmadaas(self, params):
        dts = params[FixParamTypes.DTS]
        save_dict = params[FixParamTypes.DDict]
        save_fn_fmt = params[FixParamTypes.DFnFmt]
        
        delta = params[FixParamTypes.TZ_Delta] if FixParamTypes.TZ_Delta in params else 0
        dpathexist = params[FixParamTypes.DPathExist] if FixParamTypes.DPathExist in params else True
        #时间在文件名中的格式，第一个值是源文件的，第二个是目标文件的。
        dt_fmt = params[FixParamTypes.DTFmt] if FixParamTypes.DTFmt in params else [None, None]
        f_delta = params[FixParamTypes.FDelta] if FixParamTypes.FDelta in params else None
        seqnum = params[FixParamTypes.SeqNum] if FixParamTypes.SeqNum in params else None
        seqfmt = params[FixParamTypes.SeqFmt] if FixParamTypes.SeqFmt in params else [None, None]  #[['FFF', '%03d'], ['FFF', '%03d']]

        try:
            LogLib.logger.info('FixFileInfos get_fix_file_list_with_path_cmadaas start %s' % (str(params)))

            fixfullpaths = {}
        
            for dt in dts:
                rst, savefullpath = self.getSaveFullPath(dt, save_dict, save_fn_fmt, delta=delta, seqnum=seqnum, seq_fmt=seqfmt[1], dt_fmt=dt_fmt[1], is_exist=dpathexist, f_delta=f_delta)
                if rst:
                    fixfullpaths[dt] = savefullpath
                else:
                    LogLib.logger.info('FixFileInfos get_fix_file_list_with_path_cmadaas exist %s' % (savefullpath))

            LogLib.logger.info('FixFileInfos get_fix_file_list_with_path_cmadaas over')

            return fixfullpaths
        except Exception as data:
            LogLib.logger.error('FixFileInfos get_fix_file_list_with_path_cmadaas except %s %s' % (str(params), str(data)))

            raise data
            
    #通过接口直接获得数据，根据dt和格式确定目标文件名，目标文件有多个，在不同的目录中
    def get_fix_file_list_with_path_muldstdir_cmadaas(self, params):
        dts = params[FixParamTypes.DTS]
        save_dict = params[FixParamTypes.DDict]
        save_fn_fmt = params[FixParamTypes.DFnFmt]
        
        delta = params[FixParamTypes.TZ_Delta] if FixParamTypes.TZ_Delta in params else 0
        dpathexist = params[FixParamTypes.DPathExist] if FixParamTypes.DPathExist in params else True
        #时间在文件名中的格式，第一个值是源文件的，第二个是目标文件的。
        dt_fmt = params[FixParamTypes.DTFmt] if FixParamTypes.DTFmt in params else [None, None]
        f_delta = params[FixParamTypes.FDelta] if FixParamTypes.FDelta in params else None
        seqnum = params[FixParamTypes.SeqNum] if FixParamTypes.SeqNum in params else None
        seqfmt = params[FixParamTypes.SeqFmt] if FixParamTypes.SeqFmt in params else [None, None]  #[['FFF', '%03d'], ['FFF', '%03d']]

        dir_mul_type_fmt = params[FixParamTypes.DirMulTypeFmt]

        try:
            LogLib.logger.info('FixFileInfos get_fix_file_list_with_path_cmadaas start %s' % (str(params)))

            fixfullpaths = {}
        
            for dt in dts:
                for k,v in dir_mul_type_fmt[1].items():
                    save_dict_tmp = save_dict.replace(dir_mul_type_fmt[0], v)
                    rst, savefullpath = self.getSaveFullPath(dt, save_dict_tmp, save_fn_fmt, delta=delta, seqnum=seqnum, seq_fmt=seqfmt[1], dt_fmt=dt_fmt[1], is_exist=dpathexist, f_delta=f_delta)
                    if rst:
                        if dt in fixfullpaths:
                            fixfullpaths[dt][k] = savefullpath
                        else:
                            fixfullpaths[dt] = { k:savefullpath }
                    else:
                        LogLib.logger.info('FixFileInfos get_fix_file_list_with_path_cmadaas exist %s' % (savefullpath))

            LogLib.logger.info('FixFileInfos get_fix_file_list_with_path_cmadaas over')

            return fixfullpaths
        except Exception as data:
            LogLib.logger.error('FixFileInfos get_fix_file_list_with_path_cmadaas except %s %s' % (str(params), str(data)))

            raise data
            
    #根据dt查找该dt
    #目标文件不存在，将文件名和目标文件名存入列表。
    def get_fix_file_list_with_path_file_cmadaas(self, params):
        from CMADaas.CMADaasAccess import CMADaasAccess
        from CMADaas.CMADaasError import CMADaasError

        dt = params[FixParamTypes.DT]
        url = params[FixParamTypes.Url]
        urlparams = params[FixParamTypes.UrlParams]
        time_proc = params[FixParamTypes.TimeProc]
        fix_fn_fmt = params[FixParamTypes.SFnFmt]
        save_dict = params[FixParamTypes.DDict]
        #save_fn_fmt = params[FixParamTypes.DFnFmt] 
        
        #tz_delta = params[FixParamTypes.TZ_Delta] if FixParamTypes.TZ_Delta in params else 0
        #dpathexist = params[FixParamTypes.DPathExist] if FixParamTypes.DPathExist in params else True
        #时间在文件名中的格式，第一个值是源文件的，第二个是目标文件的。
        #dt_fmt = params[FixParamTypes.DTFmt] if FixParamTypes.DTFmt in params else [None, None]
        f_delta = params[FixParamTypes.FDelta] if FixParamTypes.FDelta in params else None
        range_delta = params[FixParamTypes.RangeDelta] if FixParamTypes.RangeDelta in params else None

        try:
            LogLib.logger.info('FixFileInfos get_fix_file_list_with_path_file_cmadaas start %s' % (str(params)))
            
            urlparams['timestamp'] = str(int(datetime.datetime.now().timestamp()*1000))
            dts = [dt - datetime.timedelta(minutes=range_delta), dt]
            urlparams = time_proc(dts, urlparams, deep_copy=True)

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
            
            tmpfileinfos = {}
            for infos in rst:
                timeinfos = re.findall(fix_fn_fmt, infos['FILE_NAME'])
                if len(timeinfos) != 1:
                    #LogLib.logger.error('FixFileInfos get_fix_file_list_with_path_file_cmadaas FILE_NAME error %s %s' % (str(params), str(rst)))
                    LogLib.logger.warning('FixFileInfos get_fix_file_list_with_path_file_cmadaas FILE_NAME error %s %s' % (fix_fn_fmt, infos['FILE_NAME']))
                    #return None
                    continue

                timestr = timeinfos[0][2]
                timestrlen = len(timestr)
                if timestrlen == 6:
                    pass
                elif timestrlen == 4:
                    timestr += '00'
                elif timestrlen == 2:
                    timestr += '0000'
                else:
                    raise Exception('time error %s' % (timestr))

                k = timeinfos[0][1] + timestr
                ftime = datetime.datetime.strptime(k, '%Y%m%d%H%M%S')
                
                v = [timeinfos[0][0], ftime, infos, timeinfos[0]]

                if k in tmpfileinfos:
                    tmpfileinfos[k].append(v)
                else:
                    tmpfileinfos[k] = [v]

            fixfullpaths = {}
            for k, v in tmpfileinfos.items():
                curinfo = v[0]
                for i in range(1, len(v)):
                    if v[i][0] > curinfo[0]:
                        curinfo = v[i]

                save_path = curinfo[1].strftime(save_dict)
                savefullpath = os.path.join(save_path, curinfo[2]['FILE_NAME'])
                if not os.path.exists(save_path):
                    #os.makedirs(save_path)
                    fixfullpaths[curinfo[2]['FILE_URL']] = savefullpath
                    continue

                if os.path.exists(savefullpath):
                    LogLib.logger.info('FixFileInfos get_fix_file_list_with_path_file_cmadaas exist %s' % (savefullpath))
                    continue
                
                needdownload = True
                list_file = os.listdir(save_path)
                for fname in list_file:
                    timeinfos = re.findall(fix_fn_fmt, fname)
                    if len(timeinfos) != 1:
                        continue

                    if curinfo[3][1] == timeinfos[0][1] and curinfo[3][2] == timeinfos[0][2]:
                        if curinfo[3][0] > timeinfos[0][0]:
                            os.remove(os.path.join(save_path, fname))
                        else:
                            needdownload = False

                if needdownload:
                    fixfullpaths[curinfo[2]['FILE_URL']] = savefullpath

            LogLib.logger.info('FixFileInfos get_fix_file_list_with_path_file_cmadaas over')

            return fixfullpaths
        except Exception as data:
            LogLib.logger.error('FixFileInfos get_fix_file_list_with_path_file_cmadaas except %s %s' % (str(params), str(data)))

            raise data
            
	#回算Cassandra，源是压缩文件，压缩文件只有一个文件
    #根据dt和格式确定压缩文件名，不判断文件是否存在，确定该文件对应的目标文件是否存在。
    #目标文件不存在，将文件名和目标文件名存入列表。
    def get_fix_file_list_with_path_compress_onlyone_hs(self, params):
        dts = params[FixParamTypes.DTS]
        fix_dict = params[FixParamTypes.SDict]
        fix_fn_fmt = params[FixParamTypes.SFnFmt]
        save_dict = params[FixParamTypes.DDict]
        save_fn_fmt = params[FixParamTypes.DFnFmt]
        delta = params[FixParamTypes.TZ_Delta]
        seq_proc = params[FixParamTypes.SeqProc] if FixParamTypes.SeqProc in params else None

        try:
            LogLib.logger.info('FixFileInfos get_fix_file_list_with_path_compress_onlyone_hs start %s' % (str(params)))
            fixfullpaths = {}
        
            for dt in dts:
                fix_path = dt.strftime(fix_dict)
                list_file = os.listdir(fix_path)
                
                for fname in list_file:
                    fullpath = os.path.join(fix_path, fname)
                    if not os.path.isfile(fullpath):
                        continue

                    rersts = re.findall(fix_fn_fmt, fname)
                    if len(rersts) != 1:
                        continue

                    ftime = datetime.datetime.strptime(rersts[0][0], '%Y%m%d%H%M%S')
                    saveseqnum = int(rersts[0][1])
                    if seq_proc is not None:
                        saveseqnum = seq_proc(saveseqnum)
                    
                    rst, savefullpath = self.getSaveFullPath(ftime, save_dict, save_fn_fmt, delta=delta, seqnum=saveseqnum)
                    if rst:
                        fixfullpaths[fullpath] = savefullpath
                    else:
                        LogLib.logger.info('FixFileInfos get_fix_file_list_with_path_compress_onlyone_hs exist %s' % (savefullpath))

            LogLib.logger.info('FixFileInfos get_fix_file_list_with_path_compress_onlyone_hs over')

            return fixfullpaths
        except Exception as data:
            LogLib.logger.error('FixFileInfos get_fix_file_list_with_path_compress_onlyone_hs except %s %s' % (str(params), str(data)))

            raise data
            
    #根据dt和格式确定源路径，判断路径是否存在，如果存在，确定该文件对应的目标文件是否存在。
    #目标文件不存在，将路径和目标文件名存入列表。
    def get_fix_path_list(self, params):
        dts = params[FixParamTypes.DTS]
        fix_dict = params[FixParamTypes.SDict]
        save_dict = params[FixParamTypes.DDict]
        save_fn_fmt = params[FixParamTypes.DFnFmt]
        
        delta = params[FixParamTypes.TZ_Delta] if FixParamTypes.TZ_Delta in params else 0
        spathexist = params[FixParamTypes.SPathExist] if FixParamTypes.SPathExist in params else True
        dpathexist = params[FixParamTypes.DPathExist] if FixParamTypes.DPathExist in params else True
        #时间在文件名中的格式，第一个值是源文件的，第二个是目标文件的。
        dt_fmt = params[FixParamTypes.DTFmt] if FixParamTypes.DTFmt in params else [None, None]

        try:
            LogLib.logger.info('FixFileInfos get_fix_path_list start %s' % (str(params)))

            fixfullpaths = {}
        
            for dt in dts:
                fixfullpath = dt.strftime(fix_dict)
                if not os.path.exists(fixfullpath):
                    continue

                rst, savefullpath = self.getSaveFullPath(dt, save_dict, save_fn_fmt, delta=delta, dt_fmt=dt_fmt[1], is_exist=dpathexist)
                if rst:
                    fixfullpaths[fixfullpath] = savefullpath
                else:
                    LogLib.logger.info('FixFileInfos get_fix_path_list exist %s' % (savefullpath))

            LogLib.logger.info('FixFileInfos get_fix_path_list over')

            return fixfullpaths
        except Exception as data:
            LogLib.logger.error('FixFileInfos get_fix_path_list except %s %s' % (str(params), str(data)))

            raise data
            
    #多个源文件路径，用于检验或者数据合并等
    #根据dt和格式确定源路径，判断路径是否存在，如果存在，确定该文件对应的目标文件是否存在。
    #目标文件不存在，将路径和目标文件名存入列表。
    def get_fix_path_list_with_mulsrc(self, params):
        dt = params[FixParamTypes.DT]
        fix_dicts = params[FixParamTypes.SDicts]
        fix_fn_fmts = params[FixParamTypes.SFnFmts]
        save_dict = params[FixParamTypes.DDict]
        save_fn_fmt = params[FixParamTypes.DFnFmt]
        
        delta = params[FixParamTypes.TZ_Delta] if FixParamTypes.TZ_Delta in params else 0

        try:
            LogLib.logger.info('FixFileInfos get_fix_path_list_with_mulsrc start %s' % (str(params)))

            fixfullpaths = []
            for i in range(len(fix_dicts)):
                fix_path = dt.strftime(fix_dicts[i])
                fix_fn_fmt = dt.strftime(fix_fn_fmts[i])
                
                if not os.path.exists(fix_path):
                    LogLib.logger.warning('FixFileInfos get_fix_path_list_with_mulsrc path not exist:%s' % (fix_path))
                    return None, None

                if not os.path.isdir(fix_path):
                    LogLib.logger.error('FixFileInfos get_fix_path_list_with_mulsrc path is not dir:%s' % (fix_path))
                    return None, None

                list_file = os.listdir(fix_path)
                have_file = False
                for fname in list_file:
                    fullpath = os.path.join(fix_path, fname)

                    if re.search(fix_fn_fmt, fname) is None:
                        continue

                    if not os.path.isfile(fullpath):
                        LogLib.logger.info('FixFileInfos get_fix_path_list_with_mulsrc fullpath is not file:%s' % (fullpath))
                        #raise Exception('path is not file:%s' % fullpath)
                        continue

                    if self.minsize > 0 and os.path.getsize(fullpath) <= self.minsize:
                        LogLib.logger.error('FixFileInfos get_fix_path_list_with_mulsrc fullpath is empty:%s' % (fullpath))
                        return None, None

                    fixfullpaths.append(fullpath)
                    have_file = True
                    break

                if not have_file:
                    LogLib.logger.error('FixFileInfos get_fix_path_list_with_mulsrc path no file in path:%s' % (fix_path))
                    return None, None

            sdt = dt if delta == 0 else dt + datetime.timedelta(hours=delta)
            savefullpath = os.path.join(sdt.strftime(save_dict), sdt.strftime(save_fn_fmt))
            if os.path.exists(savefullpath):
                LogLib.logger.info('FixFileInfos get_fix_path_list_with_mulsrc exist %s' % (savefullpath))
                return '', []
            else:
                LogLib.logger.info('FixFileInfos get_fix_path_list_with_mulsrc over')
                return savefullpath, fixfullpaths
        except Exception as data:
            LogLib.logger.error('FixFileInfos get_fix_path_list_with_mulsrc except %s %s' % (str(params), str(data)))

            raise data
            
    #多个目标文件，用于将文件按照时效分成多个文件
    #根据dt和格式确定源路径，判断路径是否存在，如果存在，确定该文件对应的目标文件是否存在。
    #目标文件不存在，将路径和目标文件名存入列表。
    #如果pnumobj有值，目标文件的保存路径的字典，以str(pnum)+'_'+str(seq)为key，否则以str(seq)
    #针对只有pnum，没有seq的情况，把pnum当seq处理。
    def get_fix_path_list_with_muldst(self, params):
        dt = params[FixParamTypes.DT]
        fix_dict = params[FixParamTypes.SDict]
        fix_fn_fmt = params[FixParamTypes.SFnFmt]
        save_dict = params[FixParamTypes.DDict]
        save_fn_fmt = params[FixParamTypes.DFnFmt]
        seqobj = params[FixParamTypes.SeqObj]
        seq_fmt = params[FixParamTypes.SeqFmt]
        pnumobj = params[FixParamTypes.PNumObj] if FixParamTypes.PNumObj in params else None
        pnumfmt = params[FixParamTypes.PNumFmt] if FixParamTypes.PNumFmt in params else None
        delta = params[FixParamTypes.TZ_Delta] if FixParamTypes.TZ_Delta in params else 0

        try:
            LogLib.logger.info('FixFileInfos get_fix_path_list_with_muldst start %s' % (str(params)))

            fix_path = dt.strftime(fix_dict)
            if not os.path.exists(fix_path):
                LogLib.logger.warning('FixFileInfos get_fix_path_list_with_muldst path not exist:%s' % (fix_path))
                return None, None, None

            if not os.path.isdir(fix_path):
                LogLib.logger.error('FixFileInfos get_fix_path_list_with_muldst path is not dir:%s' % (fix_path))
                return None, None, None
            
            fullpath = os.path.join(fix_path, dt.strftime(fix_fn_fmt))

            if not os.path.exists(fullpath):
                LogLib.logger.warning('FixFileInfos get_fix_path_list_with_muldst file not exist:%s' % (fullpath))
                return None, None, None

            if not os.path.isfile(fullpath):
                LogLib.logger.info('FixFileInfos get_fix_path_list_with_muldst fullpath is not file:%s' % (fullpath))
                #raise Exception('path is not file:%s' % fullpath)
                return None, None, None

            if self.minsize > 0 and os.path.getsize(fullpath) <= self.minsize:
                LogLib.logger.error('FixFileInfos get_fix_path_list_with_muldst fullpath is empty:%s' % (fullpath))
                return None, None, None

            sdt = dt if delta == 0 else dt + datetime.timedelta(hours=delta)
            savefullpaths = {}
            savepath = sdt.strftime(save_dict)
            if pnumobj is None:
                for seqnum in seqobj:
                    savefullpaths[str(seqnum)] = os.path.join(savepath, dt.strftime(save_fn_fmt.replace(seq_fmt[1][0], seq_fmt[1][1] % seqnum)))
            else:
                for pnum in pnumobj:
                    for seqnum in seqobj:
                        tmpfn = save_fn_fmt.replace(seq_fmt[1][0], seq_fmt[1][1] % seqnum)
                        tmpfn = tmpfn.replace(pnumfmt[1][0], pnumfmt[1][1] % pnum)
                        savefullpaths[str(pnum)+'_'+str(seqnum)] = os.path.join(savepath, dt.strftime(tmpfn))

            if os.path.exists(savepath):
                slist = list(savefullpaths.items())
                for seqnum, path in slist:
                    if os.path.exists(path):
                        savefullpaths.pop(seqnum)

            if len(savefullpaths) == 0:
                LogLib.logger.info('FixFileInfos get_fix_path_list_with_muldst done %s' % (fullpath))
                return {}, '', sdt
            else:
                LogLib.logger.info('FixFileInfos get_fix_path_list_with_muldst over')
                return savefullpaths, fullpath, sdt
        except Exception as data:
            LogLib.logger.error('FixFileInfos get_fix_path_list_with_muldst except %s %s' % (str(params), str(data)))

            raise data
            
    #多个源文件，多个目标文件，用于将文件按照时效整合成成多个文件，每个目标文件中有各个源文件中该时效的数据
    #根据dt和格式确定源路径，判断路径是否存在，如果存在，确定该文件对应的目标文件是否存在。
    #目标文件不存在，将路径和目标文件名存入列表。
    #如果pnumobj有值，目标文件的保存路径的字典，以str(pnum)+'_'+str(seq)为key，否则以str(seq)
    #针对只有pnum，没有seq的情况，把pnum当seq处理。
    def get_fix_path_list_with_mulsrc_muldst(self, params):
        dt = params[FixParamTypes.DT]
        fix_dict = params[FixParamTypes.SDict]
        fix_fn_fmts = params[FixParamTypes.SFnFmt]
        save_dict = params[FixParamTypes.DDict]
        save_fn_fmt = params[FixParamTypes.DFnFmt]
        seqobj = params[FixParamTypes.SeqObj]
        seq_fmt = params[FixParamTypes.SeqFmt]
        pnumobj = params[FixParamTypes.PNumObj] if FixParamTypes.PNumObj in params else None
        pnumfmt = params[FixParamTypes.PNumFmt] if FixParamTypes.PNumFmt in params else None
        delta = params[FixParamTypes.TZ_Delta] if FixParamTypes.TZ_Delta in params else 0

        try:
            LogLib.logger.info('FixFileInfos get_fix_path_list_with_mulsrc_muldst start %s' % (str(params)))

            fix_path = dt.strftime(fix_dict)
            if not os.path.exists(fix_path):
                LogLib.logger.warning('FixFileInfos get_fix_path_list_with_mulsrc_muldst path not exist:%s' % (fix_path))
                return None, None, None

            if not os.path.isdir(fix_path):
                LogLib.logger.error('FixFileInfos get_fix_path_list_with_mulsrc_muldst path is not dir:%s' % (fix_path))
                return None, None, None
            
            fullpaths = []
            for fix_fn_fmt in fix_fn_fmts:
                fullpath = os.path.join(fix_path, dt.strftime(fix_fn_fmt))

                if not os.path.exists(fullpath):
                    LogLib.logger.warning('FixFileInfos get_fix_path_list_with_mulsrc_muldst file not exist:%s' % (fullpath))
                    return None, None, None

                if not os.path.isfile(fullpath):
                    LogLib.logger.info('FixFileInfos get_fix_path_list_with_mulsrc_muldst fullpath is not file:%s' % (fullpath))
                    #raise Exception('path is not file:%s' % fullpath)
                    return None, None, None

                if self.minsize > 0 and os.path.getsize(fullpath) <= self.minsize:
                    LogLib.logger.error('FixFileInfos get_fix_path_list_with_mulsrc_muldst fullpath is empty:%s' % (fullpath))
                    return None, None, None

                fullpaths.append(fullpath)

            sdt = dt if delta == 0 else dt + datetime.timedelta(hours=delta)
            savefullpaths = {}
            savepath = sdt.strftime(save_dict)
            
            if pnumobj is None:
                for seqnum in seqobj:
                    savefullpaths[str(seqnum)] = os.path.join(savepath, dt.strftime(save_fn_fmt.replace(seq_fmt[1][0], seq_fmt[1][1] % seqnum)))
            else:
                for pnum in pnumobj:
                    for seqnum in seqobj:
                        tmpfn = save_fn_fmt.replace(seq_fmt[1][0], seq_fmt[1][1] % seqnum)
                        tmpfn = tmpfn.replace(pnumfmt[1][0], pnumfmt[1][1] % pnum)
                        savefullpaths[str(pnum)+'_'+str(seqnum)] = os.path.join(savepath, dt.strftime(tmpfn))

            if os.path.exists(savepath):
                slist = list(savefullpaths.items())
                for seqnum, path in slist:
                    if os.path.exists(path):
                        savefullpaths.pop(seqnum)

            if len(savefullpaths) == 0:
                LogLib.logger.info('FixFileInfos get_fix_path_list_with_mulsrc_muldst done %s' % (fullpaths))
                return {}, '', sdt
            else:
                LogLib.logger.info('FixFileInfos get_fix_path_list_with_mulsrc_muldst over')
                return savefullpaths, fullpaths, sdt
        except Exception as data:
            LogLib.logger.error('FixFileInfos get_fix_path_list_with_mulsrc_muldst except %s %s' % (str(params), str(data)))

            raise data
            
    def get_sdt_from_seq(self, dt, seqcount):
        return dt + datetime.timedelta(hours=(12 - seqcount))

    #查找文件名中是指定时间的文件，并根据文件的修改时间确定是否需要读取。
    #不需要确定目标文件存不存在。
    def get_fix_file_with_modifydt(self, params):
        dt = params[FixParamTypes.DT]
        fix_dict = params[FixParamTypes.SDict]
        save_dict = params[FixParamTypes.DDict]
        fix_fn_fmt = params[FixParamTypes.SFnFmt] if FixParamTypes.SFnFmt in params else None
        save_fn_fmt = params[FixParamTypes.DFnFmt] if FixParamTypes.DFnFmt in params else None
        delta = params[FixParamTypes.TZ_Delta] if FixParamTypes.TZ_Delta in params else None
        dtinfos = params[FixParamTypes.RecordData]
        recordfdttype = params[FixParamTypes.RecordFDTType]
        recordfmdttype = params[FixParamTypes.RecordFMDTType]
        proc = params[FixParamTypes.Proc] if FixParamTypes.Proc in params else None
        seqcount = len(params[FixParamTypes.SeqObj])  if FixParamTypes.SeqObj in params else 0

        try:
            LogLib.logger.info('FixFileInfos get_fix_file_with_modifydt start %s' % (dt.strftime('%Y-%m-%d %H:%M:%S')))
            sdt = dt if delta == 0 else dt + datetime.timedelta(hours=delta)
            if proc is not None:
                sdt = proc(sdt, seqcount)

            path = dt.strftime(fix_dict)
            if not os.path.exists(path):
                LogLib.logger.info('FixFileInfos get_fix_file_with_modifydt path not exist:%s' % (path))
                return '', '', sdt

            if not os.path.isdir(path):
                LogLib.logger.error('FixFileInfos get_fix_file_with_modifydt path is not dir:%s' % (path))
                return '', '', sdt

            fullpath = os.path.join(path, dt.strftime(fix_fn_fmt))
            if not os.path.isfile(fullpath):
                LogLib.logger.error('FixFileInfos get_fix_file_with_modifydt fullpath is not file:%s' % (fullpath))
                return '', '', sdt

            if dtinfos is not None:
                if recordfdttype.value in dtinfos:
                    if dtinfos[recordfdttype.value] == dt.strftime('%Y%m%d%H%M%S') and dtinfos[recordfmdttype.value] == int(os.path.getmtime(fullpath)):
                        LogLib.logger.info('FixFileInfos get_fix_file_with_modifydt not need proc:%s' % (fullpath))
                        return '', '', sdt

            if self.minsize > 0 and os.path.getsize(fullpath) <= self.minsize:
                LogLib.logger.info('FixFileInfos get_fix_file_with_modifydt fullpath is empty:%s' % (fullpath))
                return '', '', sdt

            savefullpath = os.path.join(sdt.strftime(save_dict), sdt.strftime(save_fn_fmt))

            LogLib.logger.info('FixFileInfos get_fix_file_with_modifydt over')

            return savefullpath, fullpath, sdt
        except Exception as data:
            LogLib.logger.error('FixFileInfos get_fix_file_with_modifydt except %s %s' % (dt.strftime('%Y-%m-%d %H:%M:%S'), str(data)))

            raise data
        
    def __get_fullpath(self, dt, fix_dict_, fix_fn_fmt_):
        fix_path = dt.strftime(fix_dict_)
        fix_fn_fmt = dt.strftime(fix_fn_fmt_)
        
        if not os.path.exists(fix_path):
            LogLib.logger.warning('FixFileInfos __get_fullpath path not exist:%s' % (fix_path))
            return None

        if not os.path.isdir(fix_path):
            LogLib.logger.error('FixFileInfos __get_fullpath path is not dir:%s' % (fix_path))
            return None

        fullpath = os.path.join(fix_path, fix_fn_fmt)
        
        if not os.path.isfile(fullpath):
            LogLib.logger.error('FixFileInfos __get_fullpath fullpath is not file:%s' % (fullpath))
            return None

        if self.minsize > 0 and os.path.getsize(fullpath) <= self.minsize:
            LogLib.logger.error('FixFileInfos __get_fullpath fullpath is empty:%s' % (fullpath))
            return None

        return fullpath

    #多个源文件路径，一个预报，多个时间的实况
    #根据dt和格式确定源路径，判断路径是否存在。
    #dts_list格式为[[dt,[dt1,dt1,...]],[dt,[dt1,dt1...]],...]，dt也可以是列表，每个项对应fix_dicts和fix_fn_fmts.
    def get_fix_path_list_with_multime(self, params):
        dts_list = params[FixParamTypes.DTS]
        fix_dicts = params[FixParamTypes.SDicts]
        fix_fn_fmts = params[FixParamTypes.SFnFmts]
        save_dict = params[FixParamTypes.DDict]
        save_fn_fmt = params[FixParamTypes.DFnFmt]
        
        try:
            LogLib.logger.info('FixFileInfos get_fix_path_list_with_multime start %s' % (str(params)))

            fixfullpaths = []
            for dts in dts_list:
                fullpaths = []
                for i in range(len(dts)):
                    tmpdts = dts[i]
                    if type(tmpdts) is datetime.datetime:
                        fullpath = self.__get_fullpath(tmpdts, fix_dicts[i], fix_fn_fmts[i])
                        fullpaths.append(fullpath)
                    elif type(tmpdts) is list:
                        rst = []
                        for dt in tmpdts:
                            fullpath = self.__get_fullpath(dt, fix_dicts[i], fix_fn_fmts[i])
                            rst.append(fullpath)

                        fullpaths.append(rst)
                    else:
                        raise Exception('unknown dts')

                fixfullpaths.append(fullpaths)

            savefullpath = os.path.join(save_dict, save_fn_fmt)

            LogLib.logger.info('FixFileInfos get_fix_path_list_with_multime over')
            return savefullpath, fixfullpaths
        except Exception as data:
            LogLib.logger.error('FixFileInfos get_fix_path_list_with_multime except %s %s' % (str(params), str(data)))

            raise data

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

    
    def get_save_filename(self, dt, save_dict, save_fn_fmt, save_seq, save_seq_fmt, save_fhs, fhsdelta):
        tmpdt = dt
        tmpdt += datetime.timedelta(minutes=fhsdelta)

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


    #多个源文件路径，找各自的最后一个文件
    #根据dt和格式确定源路径，判断路径是否存在。
    def get_fix_path_list_last(self, params):
        dt = params[FixParamTypes.DT]
        fix_dict = params[FixParamTypes.SDict]
        fix_fn_fmt = params[FixParamTypes.SFnFmt]
        fix_seq = params[FixParamTypes.SSeq]
        fix_fhs = params[FixParamTypes.SFHS]
        sfdelta = params[FixParamTypes.SFDelta] if FixParamTypes.SFDelta in params else None

        save_dict = params[FixParamTypes.DDict]
        save_fn_fmt = params[FixParamTypes.DFnFmt]
        save_seq = params[FixParamTypes.DSeq]
        save_seq_fmt = params[FixParamTypes.DSeqFmt]
        save_fhs = params[FixParamTypes.DFHS]
        dfhsdelta = params[FixParamTypes.DFhsDelta] if FixParamTypes.DFhsDelta in params else 0

        try:
            LogLib.logger.info('FixFileInfos get_fix_path_list_last start %s' % (str(params)))
            filedt, fullpath = self.get_last_filename(dt, fix_dict, fix_fn_fmt, fix_seq, fix_fhs, sfdelta)
            if filedt is None or fullpath is None:
                return (None, None, None)

            saveinfos = {}
            savedt, savefullpaths = self.get_save_filename(dt, save_dict, save_fn_fmt, save_seq, save_seq_fmt, save_fhs, dfhsdelta)
            if len(savefullpaths) > 0:
                for seq,path in savefullpaths.items():
                    fseq = int((savedt + datetime.timedelta(hours=seq) - filedt).total_seconds() / 3600)
                    if fseq in fix_seq:
                        saveinfos[str(fseq)] = path
                    else:
                        LogLib.logger.warning('FixFileInfos get_fix_path_list_last no seq %s %s %s %s %s' % (str(filedt), str(savedt), str(seq), fullpath, path))
            else:
                LogLib.logger.info('FixFileInfos get_fix_path_list_last not need save %s %s %s' % (str(filedt), str(savedt), fullpath))

            LogLib.logger.info('FixFileInfos get_fix_path_list_last over')

            return (saveinfos, fullpath, savedt)
        except Exception as data:
            LogLib.logger.error('FixFileInfos get_fix_path_list_last except %s %s' % (str(params), str(data)))

            raise data
            
if __name__ == '__main__':
    print('done')
