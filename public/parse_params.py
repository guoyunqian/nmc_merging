#!/usr/bin/python
# -*- coding: utf-8 -*-
#Filename: parse_params.py

'''
Created on Mar 29, 2021

@author: anduin
'''

import sys
import datetime
import getopt
from configparser import ConfigParser

from publictype.fixparamtypes import FixParamTypes

#转换类似20210120这样的字符串为datetime
def parse_dt_format(dtstr):
    slen = len(dtstr)
    if slen == 4:
        return datetime.datetime.strptime(dtstr, '%Y')
    if slen == 6:
        return datetime.datetime.strptime(dtstr, '%Y%m')
    if slen == 8:
        return datetime.datetime.strptime(dtstr, '%Y%m%d')
    if slen == 10:
        return datetime.datetime.strptime(dtstr, '%Y%m%d%H')
    if slen == 12:
        return datetime.datetime.strptime(dtstr, '%Y%m%d%H%M')
    if slen == 14:
        return datetime.datetime.strptime(dtstr, '%Y%m%d%H%M%S')
    else:
        raise Exception('error dt string %s' % dtstr)
    
#'-d': 日期，如：'-d 2days', '-d 20210120', '-d 20201125,20201126'，北京时
#'-u': 日期，如：'-u 2days', '-u 20210120', '-u 20201125,20201126'，世界时
#以当前时间为基准的，若干时间之内的配置，只支持整数的days、hours、minutes，并且大于0。
#支持当前时间前若干时间的时间段，支持单个时间点，支持开始结束时间的时间段，
#不支持单个时间的序列，对于时间段，获得需要处理的时间点时，根据选择函数的不同（正序和倒序），
#会不包含开始时间或者结束时间
def parse_dt(param_str, is_bj=True):
    if param_str is None or len(param_str) == 0:
        raise Exception('error format %s' % param_str)

    dt_start = None
    dt_end = None

    tmpstr = ''
    for i in range(len(param_str)):
        c = param_str[i]
        if c >= '0' and c <= '9':
            tmpstr += c
        elif c == ',':
            if dt_start is None:
                dt_start = parse_dt_format(tmpstr)
                tmpstr = ''
            else:
                raise Exception('error format %s' % param_str)
        elif c in ['d', 'h', 'm']:
            if dt_start is None or dt_end is not None:
                raise Exception('error format %s' % param_str)

            tmpnum = int(tmpstr)
            if tmpnum == 0:
                raise Exception('error format %s' % param_str)

            if is_bj:
                dt_end = datetime.datetime.now()
            else:
                dt_end = datetime.datetime.utcnow()

            tmpstr = param_str[i:]
            if tmpstr == 'days':
                dt_start = dt_end - datetime.timedelta(days=tmpnum)
            elif tmpstr == 'hours':
                dt_start = dt_end - datetime.timedelta(hours=tmpnum)
            elif tmpstr == 'minutes':
                dt_start = dt_end - datetime.timedelta(minutes=tmpnum)
            else:
                raise Exception('error format %s' % param_str)

            tmpstr = ''
        else:
            raise Exception('error format %s' % param_str)

    if len(tmpstr) > 0:
        if dt_start is None:
            dt_start = parse_dt_format(tmpstr)
        elif dt_end is None:
            dt_end = parse_dt_format(tmpstr)
        else:
            raise Exception('error format %s' % param_str)

    return (dt_start, dt_end)


#'-b': 起报时，如：'-b 08,20'，对应fhs
#'-t': 与起报时一起确定需要处理的每个时刻的文件，同-b格式相同，对应fms
#'-s': 时效，与-b格式相同，对应seqobj
#格式说明：a,b,c:d:e,f:g,h，逗号分开每个值，冒号分开部分为一个整体，用来生成序列，同range
#对于区间的类型，当前只支持数值类型，right_c默认为False，不包括右值，如果为True，则用range获得列表时，需要将结束值加1
#区间类型
def parse_list(param_str, is_num=True, right_c=False):
    rst = []
    v_list = param_str.split(',')
    for v in v_list:
        if v.find(':') > 0:
            s_list = v.split(':')
            slen = len(s_list)
            if slen == 2 or slen == 3:
                stop = int(s_list[1]) + 1 if right_c else int(s_list[1])
                step = 1 if slen == 2 else int(s_list[2])

                rst.extend(list(range(int(s_list[0]), stop, step)))
            else:
                raise Exception('format error %s' % (v))
        else:
            if is_num:
                rst.append(int(v))
            else:
                rst.append(v)

    return rst

#'-f': 配置文件名，如：'-f config.ini'，注意不带路径，通常和程序放在同一目录，暂不需要
#'-o': 覆盖生成，如：'-o'，注意后面不加任何内容，如果存在则设置key为DPathExist的项为False，默认是True，不覆盖


def parse_prog_params(params=None, logger=None):
    try:
        short_params = "d:u:b:t:s:f:l:o"
        long_params = ['d-is-bjt=','','']

        if params is None:
            params = {}

        opts, args = getopt.getopt(sys.argv[1:], short_params, long_params)
        for opt, arg in opts:
            if opt == '-d':
                params[FixParamTypes.SIsBJT] = True
                params[FixParamTypes.STime], params[FixParamTypes.ETime] = parse_dt(arg)
            elif opt == '-u':
                params[FixParamTypes.SIsBJT] = False
                params[FixParamTypes.STime], params[FixParamTypes.ETime] = parse_dt(arg, is_bj=False)
            elif opt == '--d-is-bjt':
                if arg.lower() == 'true':
                    params[FixParamTypes.DIsBJT] = False
                elif arg.lower() == 'false':
                    params[FixParamTypes.DIsBJT] = False
                else:
                    raise Exception('--d-is-bjt is error %s' % arg)
            elif opt == '-b':
                params[FixParamTypes.FHS] = arg
            elif opt == '-l':
                params[FixParamTypes.LogFilePath] = arg
            elif opt == '-f':
                params[FixParamTypes.CfgFilePath] = arg
            elif opt == '-o':
                params[FixParamTypes.DPathExist] = False
            else:
                print("参数错误：%s == %s>" % (opt, arg))
                if logger:
                    logger.error('parse_prog_params params error:%s == %s>' % (opt, arg))

                return None

        return params
    except Exception as data:
        print("获取参数错误")
        if logger:
            logger.error('parse_prog_params except:%s' % (str(data)))

        return None
    
#读取ini文件中的时间设置，格式如parse_dt中介绍。
def get_dt_range(section, option):
    if cfg.has_option(section, option):
        dt_start, dt_end = parse_dt(cfg.get(section, option))
        if dt_start is None and dt_end is None:
            return None
        else:
            return (dt_start, dt_end)
    else:
        return None
    
#读取ini文件中的字符串类型设置
def get_opt_str(cfg, section, option):
    if cfg.has_option(section, option):
        return cfg.get(section, option)
    else:
        return None
    
#读取ini文件中的整数类型设置
def get_opt_int(cfg, section, option):
    if cfg.has_option(section, option):
        rst = cfg.get(section, option)
        if rst == '':
            return None
        else:
            return int(rst)
    else:
        return None

#读取ini文件中的字符串类型设置
def get_opt_float(cfg, section, option):
    if cfg.has_option(section, option):
        rst = cfg.get(section, option)
        if rst == '':
            return None
        else:
            return float(rst)
    else:
        return None

#多个相同的，采用名字加格式化序号的option，返回设置列表
#序号需要是连续的，一旦中断，视为末尾
def parse_ini_mulinfos(cfg, sectionname, optnamefmt):
    infos = []

    for i in range(1, 100):
        tmpname = optnamefmt % i
        if cfg.has_option(sectionname, tmpname):
            info = cfg.get(sectionname, tmpname)
            if info == '':
                info = None
            infos.append(info)
        else:
            break

    return infos

def parse_ini_section_mulinfos(params, cfg, sectionname, optnamefmt, singlename, mulname, s_optnamefmt, s_singlename, s_mulname):
    if cfg.has_section(sectionname):
        infos = parse_ini_mulinfos(cfg, sectionname, optnamefmt)
        dlen = len(infos)
        if dlen == 1:
            params[singlename] = infos[0]
        elif dlen > 1:
            params[mulname] = infos
                
        infos = parse_ini_mulinfos(cfg, sectionname, s_optnamefmt)
        dlen = len(infos)
        if dlen == 1:
            params[s_singlename] = infos[0]
        elif dlen > 1:
            params[s_mulname] = infos
                
'''            
def parse_ini_params(inipath, params=None, logger=None):
    try:
        if params is None:
            params = {}

        cfg = ConfigParser()
        cfg.read(inipath)
        
        #print(cfg.sections())
        dtrange = get_dt_range('dt', 'time_range')
        if dtrange is not None:
            params[FixParamTypes.STime] = dt_start
            params[FixParamTypes.ETime] = dt_end

        parse_ini_section_mulinfos(params, cfg, 'Path', 'Info%02d', FixParamTypes.SDict, FixParamTypes.SDicts, 'Save%02d', FixParamTypes.DDict, FixParamTypes.DDicts)
        parse_ini_section_mulinfos(params, cfg, 'Fn_Fmt', 'Info%02d', FixParamTypes.SFnFmt, FixParamTypes.SFnFmts, 'Save%02d', FixParamTypes.DFnFmt, FixParamTypes.DFnFmts)
        parse_ini_section_mulinfos(params, cfg, 'FHS', 'Info%02d', FixParamTypes.SFHS, FixParamTypes.SFHSs, 'Save%02d', FixParamTypes.DFHS, FixParamTypes.DFHSs)
        parse_ini_section_mulinfos(params, cfg, 'Seq', 'Info%02d', FixParamTypes.SSeq, FixParamTypes.SSeqs, 'Save%02d', FixParamTypes.DSeq, FixParamTypes.DSeqs)
        parse_ini_section_mulinfos(params, cfg, 'Seq_Fmt', 'Info%02d', FixParamTypes.SSeqFmt, FixParamTypes.SSeqFmts, 'Save%02d', FixParamTypes.DSeqFmt, FixParamTypes.DSeqFmts)
        parse_ini_section_mulinfos(params, cfg, 'FDelta', 'Info%02d', FixParamTypes.SFDelta, FixParamTypes.SFDeltas, 'Save%02d', FixParamTypes.DFDelta, FixParamTypes.DFDeltas)
        parse_ini_section_mulinfos(params, cfg, 'Fhs_Delta', 'Info%02d', FixParamTypes.SFhsDelta, FixParamTypes.SFhsDeltas, 'Save%02d', FixParamTypes.DFhsDelta, FixParamTypes.DFhsDeltas)
        
        if cfg.has_option('RecordFile', 'RecordPath'):
            params[FixParamTypes.RecordPath] = cfg.get('RecordFile', 'RecordPath')

        return params
    except Exception as data:
        print("获取参数错误")
        if logger:
            logger.error('parse_ini_params except:%s' % (str(data)))

        return None
    '''

#解析ini文件，返回ConfigParser对象
def parse_ini_file(inipath, logger=None):
    try:
        cfg = ConfigParser()
        cfg.read(inipath, encoding='utf8')
        
        return cfg
    except Exception as data:
        print("获取参数错误")
        if logger:
            logger.error('parse_ini_file except:%s' % (str(data)))

        return None


if __name__ == '__main__':
    print(parse_prog_params())

    print('test done')


