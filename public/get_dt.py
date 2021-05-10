#!/usr/bin/python
# -*- coding: utf-8 -*-
#Filename: get_dt.py

'''
Created on Jan 21, 2021

@author: anduin
'''

import datetime
import re

def get_dt_from_fname_with_re(fname, patt, dtfmt):
    rsts = re.findall(patt, fname)
    if len(rsts) != 1:
        raise Exception('patt or fname error')

    return datetime.datetime.strptime(rsts[0], dtfmt)

#往前找最近的星期一或者星期四，包括当前天，weekday是curdt的weekday。
def get_dt_with_ec_includecur(curdt):
    wd = curdt.weekday()
    if wd == 0 or wd == 3:
        return curdt
    elif wd < 3:
        return curdt - datetime.timedelta(days=wd)
    else: # wd > 3
        return curdt - datetime.timedelta(days=wd-3)
    
#往后找最近的星期一或者星期四，包括当前天，weekday是curdt的weekday。
def get_dt_with_ec_includecur_next(curdt):
    wd = curdt.weekday()
    if wd == 0 or wd == 3:
        return curdt
    elif wd < 3:
        return curdt + datetime.timedelta(days=3-wd)
    else: # wd > 3
        return curdt + datetime.timedelta(days=7-wd)
    
#往前找最近的星期一或者星期四，不包括当前天
def get_dt_with_ec_not_includecur(curdt):
    wd = curdt.weekday()
    if wd == 0:
        return curdt - datetime.timedelta(days=4)
    elif wd <= 3:
        return curdt - datetime.timedelta(days=wd)
    else: # wd > 3
        return curdt - datetime.timedelta(days=wd-3)
    
#往后找最近的星期一或者星期四，不包括当前天
def get_dt_with_ec_not_includecur_next(curdt):
    wd = curdt.weekday()
    if wd < 3:
        return curdt + datetime.timedelta(days=3-wd)
    else: # wd >= 3
        return curdt + datetime.timedelta(days=7-wd)

#找指定的前若干年的每个指定日期，如果指定的天是闰年的2月29，则找2月28
def get_dts_withec(curdt, dtcount):
    year = curdt.year
    month = curdt.month
    day = curdt.day

    if month == 2 and day == 29:
        day = 28

    #year -= 1

    dts = []
    for i in range(dtcount):
        year -= 1
        dts.append(datetime.datetime(year, month, day, 0, 0, 0, 0))

    return dts


if __name__ == '__main__':
    print(get_dts_withec(datetime.datetime.now(), 20))

    print('test done')


