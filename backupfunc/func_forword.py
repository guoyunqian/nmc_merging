#!/usr/bin/python
# -*- coding: utf-8 -*-
#Filename: func_diff_value_num.py

"""
Created on May 13, 2021

@author: anduin
"""

import os
import shutil
import datetime

import public
from publictype.fixparamtypes import FixParamTypes

func_name = 'forword'

def get_params(cfg, section, params, logger):
    #往回找的时间列表
    rst = public.get_opt_str(cfg, section, 'timedelta')
    if rst is None:
        raise Exception('forword %s timedelta error' % section)

    deltas = public.parse_list(rst, is_num=True, right_c=True)

    params[FixParamTypes.Deltas] = deltas
    
'''
def run_func(params, logger):
    #filename, dt, seq, seq_field, level_field=None, data_name='data0', gribrst=True

    path = params[FixParamTypes.SDict]
    fn_fmt = params[FixParamTypes.SFnFmt]
    dt = params[FixParamTypes.dt]
    deltas = params[FixParamTypes.Deltas]
    

    filename = public.get_path_with_replace()

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


    filename = params[FixParamTypes.SFullPath]
    seq = params[FixParamTypes.SeqObj]
    seq_field = params[FixParamTypes.SeqField]
    level_field = params[FixParamTypes.LevelField] if FixParamTypes.LevelField in params else None
    data_name = params[FixParamTypes.DName] if FixParamTypes.DName in params else 'data0'
    gribrst = params[FixParamTypes.GribRst] if FixParamTypes.GribRst in params else True

    needseq = []
    needseq.extend(seq)
    '''



if __name__ == '__main__':
    print('done')
