#!/usr/bin/python
# -*- coding: utf-8 -*-
#Filename: get_dt.py

'''
Created on Jan 21, 2021

@author: anduin
'''

import os

#workdir、defaultdir和defaultfn是fn为None或者只是文件名字时填充目录和文件名
#fn要么是None，空字符，要么一定要有文件名
def get_path_infos(fn, workdir=None, defaultdir=None, defaultfn=None, create_dir=True):
    dir = None
    filename = None

    if fn is None or len(fn) == 0:
        if workdir is None or len(workdir.strip()) == 0 or defaultfn is None or len(defaultfn.strip()) == 0:
            raise Exception('workdir or defaultfn is None')
        
        if defaultdir is None or len(defaultdir.strip()) == 0:
            dir = workdir
        else:
            dir = os.path.join(workdir, defaultdir)

        filename = os.path.join(dir, defaultfn)
    else:
        dir, fname = os.path.split(fn)
        if dir == '':
            if defaultdir is None or len(defaultdir.strip()) == 0:
                dir = workdir
            else:
                dir = os.path.join(workdir, defaultdir)

            filename = os.path.join(dir, fname)
        elif os.path.isabs(dir):
            filename = fn
        else:
            dir = os.path.abspath(dir)
            filename = os.path.abspath(fn)

    if create_dir:
        if not os.path.exists(dir):
            os.makedirs(dir)

    return(dir, filename)

full_year_fmt = '[YYYY]'
year_fmt = '[yy]'
month_fmt = '[mm]'
day_fmt = '[dd]'
hour_fmt = '[HH]'
minute_fmt = '[MM]'
second_fmt = '[SS]'
seq_fmt_03 = '[FFF]'
seq_fmt_04 = '[FFFF]'

#
def get_path_with_replace(path_or_filename, dt=None, seq=None):
    if dt is not None:
        if path_or_filename.find(full_year_fmt) >= 0:
            path_or_filename = path_or_filename.replace(full_year_fmt, ('%04d' % dt.year))
        
        if path_or_filename.find(year_fmt) >= 0:
            path_or_filename = path_or_filename.replace(year_fmt, ('%04d' % dt.year)[2:])

        if path_or_filename.find(month_fmt) >= 0:
            path_or_filename = path_or_filename.replace(month_fmt, ('%02d' % dt.month))
            
        if path_or_filename.find(day_fmt) >= 0:
            path_or_filename = path_or_filename.replace(day_fmt, ('%02d' % dt.day))

        if path_or_filename.find(hour_fmt) >= 0:
            path_or_filename = path_or_filename.replace(hour_fmt, ('%02d' % dt.hour))

        if path_or_filename.find(minute_fmt) >= 0:
            path_or_filename = path_or_filename.replace(minute_fmt, ('%02d' % dt.minute))

        if path_or_filename.find(second_fmt) >= 0:
            path_or_filename = path_or_filename.replace(second_fmt, ('%02d' % dt.second))
            
    if seq is not None:
        if path_or_filename.find(seq_fmt_03) >= 0:
            path_or_filename = path_or_filename.replace(seq_fmt_03, ('%03d' % seq))
        elif path_or_filename.find(seq_fmt_04) >= 0:
            path_or_filename = path_or_filename.replace(seq_fmt_04, ('%04d' % seq))
            
    return path_or_filename

if __name__ == '__main__':

    print('test done')


