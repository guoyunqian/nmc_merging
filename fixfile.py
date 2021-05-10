#!/usr/bin/python
# -*- coding: utf-8 -*-
#Filename: fixfile.py

"""
Created on Nov 4, 2020

@author: anduin
"""

import os
import datetime
import shutil

from logmodule.loglib import *

def delete_tree(filepath, curdate, days=7, dir_fmt=r'%Y%m%d'):
    try:
        procdate = curdate - datetime.timedelta(days=days)
        
        LogLib.logger.info('delete_tree start %s' % (procdate.strftime('%Y-%m-%d %H:%M:%S')))

        for fn in os.listdir(filepath):
            fullpath = os.path.join(filepath, fn)
            if os.path.isdir(fullpath):
                dt = datetime.datetime.strptime(fn, dir_fmt)
                if dt <= procdate:
                    shutil.rmtree(fullpath)
                    LogLib.logger.info('compress_dir rmtree %s' % (fullpath))
    except Exception as data:
        LogLib.logger.error('delete_tree except %s' % (str(data)))
                
def delete_files(filepath, curdate, days=7, proc_days=5, dir_fmt=r'%Y%m%d', file_fmt=r'm01_([0-9]{12}).m3'):
    import re

    try:
        procdate = curdate - datetime.timedelta(days=days)
        
        LogLib.logger.info('delete_files start %s' % (procdate.strftime('%Y-%m-%d %H:%M:%S')))

        for fn in os.listdir(filepath):
            fullpath = os.path.join(filepath, fn)
            if os.path.isdir(fullpath):
                dt = datetime.datetime.strptime(fn, dir_fmt)
                if proc_days is not None and dt > procdate - datetime.timedelta(days=proc_days):
                    continue

                if dt <= procdate:
                    for fi in os.listdir(fullpath):
                        fullfilepath = os.path.join(fullpath, fi)
                        if os.path.isfile(fullfilepath):
                            rsts = re.findall(file_fmt, fi)
                            if len(rsts) == 1:
                                os.remove(fullfilepath)
                                LogLib.logger.info('compress_dir remove over %s' % (fullfilepath))
    except Exception as data:
        LogLib.logger.error('delete_files except %s' % (str(data)))

def compress_dir(filepath, curdate, output_path, days=7, dir_fmt=r'%Y%m%d', file_fmt=r'm01_%Y%m%d.gz'):
    from public import zip_file_path

    try:
        procdate = curdate - datetime.timedelta(days=days)

        LogLib.logger.info('compress_dir start %s' % (procdate.strftime('%Y-%m-%d %H:%M:%S')))

        for fn in os.listdir(filepath):
            fullpath = os.path.join(filepath, fn)
            if os.path.isdir(fullpath):
                dt = datetime.datetime.strptime(fn, dir_fmt)
                if dt <= procdate:
                    output_file = dt.strftime(file_fmt)
                    savepath = os.path.join(output_path, output_file)
                    if not os.path.exists(savepath):
                        tmpfile = savepath + '.tmp'
                        if not zip_file_path(fullpath, tmpfile):
                            LogLib.logger.error('compress_dir zip_file_path error %s %s' % (fullpath, savepath))
                            continue

                        shutil.move(tmpfile, savepath)

                        LogLib.logger.info('compress_dir compress over %s' % (savepath))

                    shutil.rmtree(fullpath)

                    LogLib.logger.info('compress_dir rmtree %s' % (fullpath))

    except Exception as data:
        LogLib.logger.error('compress_dir except %s' % (str(data)))

                

#日志文件存储目录
log_file_dir = 'logfiles'
#日志文件的文件名
log_file_name = 'fixfile.log'

def init_log(workdir):
    logdir = os.path.join(workdir, log_file_dir)
    if not os.path.exists(logdir):
        os.mkdir(logdir)

    LogLib.init()
    LogLib.addTimedRotatingFileHandler(os.path.join(logdir, log_file_name))
    LogLib.setLevel(logging.DEBUG)
    
def uninit_log():
    LogLib.uninit()
    
def proc():
    curdate = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    #fix_dict = r'C:\testdata\deltest\compress'
    fix_dict = r'E:\QPE\SUR_01min_bak'
    #save_dict = r'C:\testdata\deltest\compress'
    save_dict = r'E:\QPE\SUR_01min_bak'
    delta_t = 10   #天
    dir_fmt = r'%Y%m%d'
    file_fmt='m01_%Y%m%d.gz'

    compress_dir(fix_dict, curdate, save_dict, days=delta_t, dir_fmt=dir_fmt, file_fmt=file_fmt)

    
    #fix_dict = r'C:\testdata\deltest\del'
    fix_dict = r'E:\QPE\SUR_10min'
    delta_t = 10   #天
    proc_days = 5  #天
    dir_fmt = r'%Y%m%d'
    file_fmt = r'm01_([0-9]{12}).m3'

    delete_files(fix_dict, curdate, days=delta_t, proc_days=proc_days, dir_fmt=dir_fmt, file_fmt=file_fmt)


if __name__ == '__main__':
    
    workdir = os.path.dirname(__file__)
    init_log(workdir)

    proc()
    
    uninit_log()

    print('done')
