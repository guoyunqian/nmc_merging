#!/usr/bin/python
# -*- coding: utf-8 -*-
#Filename: get_stations.py

'''
Created on Mar 1, 2021

@author: anduin
'''

import pandas as pd


def convert_sta_id_to_int(staidstr):
    staid = 0

    for c in staidstr:
        if c >= '0' and c <= '9':
            staid = staid * 10 + int(c)
        else:
            staid = staid * 100 + ord(c)

    return staid

#54398  116.62   40.13  54398 北京
def get_stations_from_csv(station_file, dropcol=[1, 2, 3, 4], columns=None):
    stations = pd.read_csv(station_file, header=None, sep="\\s+") #, index_col=0)
    #stations[1] = default
    stations.drop(dropcol, axis=1, inplace=True)

    if columns is not None:
        stations.columns = columns

    return stations


if __name__ == '__main__':
    print('test done')


