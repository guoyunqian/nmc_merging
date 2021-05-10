#!/usr/bin/python
# -*- coding: utf-8 -*-
#Filename: gribtypes.py

'''
Created on Apr 22, 2021

@author: anduin
'''

from enum import Enum

class GribTypes(Enum):
    #grib文件中对应seq的字段
    endStep = 'endStep'
    stepRange = 'stepRange'

    #grib文件中对于扰动预报序号的字段
    perturbationNumber = 'perturbationNumber'


if __name__ == '__main__':
    a = GribTypes.endStep
    print(a.value)
    print(GribTypes.endStep)
    
    print('test done')