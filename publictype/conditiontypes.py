#!/usr/bin/python
# -*- coding: utf-8 -*-
#Filename: conditiontypes.py

'''
Created on Nov 14, 2020

@author: anduin
'''

from enum import Enum
class ConditionTypes(Enum):
    Greater = 1
    Less = 2
    Equal  = 3
    Not_Greater = 4
    Not_Less = 5
    Not_Equal = 6
    Nan = 7
    Not_Nan = 8
    In = 9
    Not_in = 10

if __name__ == '__main__':
    
    a=ConditionTypes.less
    print(a.value)
    print(ConditionTypes.less)
    
    print('test done')