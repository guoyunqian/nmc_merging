#!/usr/bin/python
# -*- coding: utf-8 -*-
#Filename: fixproctypes.py

'''
Created on Aug 21, 2020

@author: anduin
'''

from enum import Enum
class FixProcTypes(Enum):
    #根据参数确定需要处理的时间点
    DTList = 'dtlist'
    #根据参数确定处理的文件，以及需要保存的文件路径
    FileList = 'filelist'
    #根据参数读出文件或者网络或者云平台数据
    ReadData = 'readdata'
    #根据参数，对读出的数据进行处理，插值、默认值等
    ModifyData = 'modifydata'
    #根据参数，对数据进行合并、加减等操作，存在2个或者多个数据集，数据集第一个为需要返回的数据集
    MulData = 'muldata'
    #根据参数，将数据集保存到文件或者网络或者云平台等
    WriteData = 'writedata'
    #记录处理的信息，比如上次处理文件的时效、修改时间
    RecordData = 'recorddata'

if __name__ == '__main__':
    
    a = FixProcTypes.DTList
    print(a.value)
    print(a.name)
    print(FixProcTypes.ReadData)
    
    print(FixProcTypes['WriteData'])
    print(FixProcTypes('modifydata'))
    
    print('test done')