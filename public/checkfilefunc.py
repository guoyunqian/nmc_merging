#!/usr/bin/python
# -*- coding: utf-8 -*-
#Filename: checkfilefunc.py

"""
Created on Nov 4, 2020

@author: anduin
"""

import os
import shutil
import datetime

def check_allfile_size(filepath, fsize=1024*1024):
    for fn in os.listdir(filepath):
        fullpath = os.path.join(filepath, fn)
        if os.path.isdir(fullpath):
            check_allfile_size(fullpath)

        if os.path.isfile(fullpath):
            if os.path.getsize(fullpath) < fsize:
                print(fullpath)

def rename_to_bt(filepath):
    for fn in os.listdir(filepath):
        fullpath = os.path.join(filepath, fn)
        if os.path.isdir(fullpath):
            rename_to_bt(fullpath)

        if os.path.isfile(fullpath):
            if fn[:2] != 'BT':
                os.rename(fullpath, os.path.join(filepath, 'BT' + fn))
                
def check_allfile_count(filepath, depth=0):
    filecount = 0
    for fn in os.listdir(filepath):
        fullpath = os.path.join(filepath, fn)
        if os.path.isdir(fullpath):
            check_allfile_count(fullpath, depth+1)

        if os.path.isfile(fullpath):
            filecount += 1

    infostr = ''
    for i in range(depth):
        infostr += '  '

    print('%s%s:%d' % (infostr, filepath, filecount))

def rename_with_dt(stime, etime, path, nameinfos):
    while stime <= etime:
        fullpath = stime.strftime(path)
        stime += datetime.timedelta(days=1)
        if not os.path.exists(fullpath):
            continue

        for infos in nameinfos:
            sname = infos[0]
            dname = infos[1]

            spath = os.path.join(fullpath, sname)
            if os.path.exists(spath):
                shutil.move(spath, os.path.join(fullpath, dname))
                print(fullpath)
                
def deletefiles(filepath, curdate, days=7, dir_fmt=r'%Y%m%d'):
    deldate = curdate - datetime.timedelta(days=days)
    fullpath = deldate.strftime(filepath)

    if not os.path.exists(fullpath):
        print('fullpath is not exist %s' % fullpath)
        return

    for fn in os.listdir(fullpath):
        curpath = os.path.join(fullpath, fn)
        if os.path.isdir(curpath):
            dt = datetime.datetime.strptime(fn, dir_fmt)
            if dt <= deldate:
                shutil.rmtree(curpath)
                print('curpath is deleted %s' % curpath)
        else:
            print('curpath is not dir %s' % curpath)

if __name__ == '__main__':
    print('done')
