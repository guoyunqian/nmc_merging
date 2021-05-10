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

if __name__ == '__main__':

    print('test done')


