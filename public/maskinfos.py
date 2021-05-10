#!/usr/bin/python
# -*- coding: utf-8 -*-
#Filename: maskinfos.py

'''
Created on Mar 3, 2021

@author: anduin
'''

'''
a = "11  BEPK     北京市 "\
"12  BETJ     天津市 "\
"13  BESZ     河北省          "\
"14  BETY     山西省          "\
"15  BEHT     内蒙古自治区    "\
"21  BCSY     辽宁省          "\
"22  BECC     吉林省          "\
"23  BEHB     黑龙江省        "\
"31  BCSH     上海市          "\
"32  BENJ     江苏省          "\
"33  BEHZ     浙江省          "\
"34  BEHF     安徽省          "\
"35  BEFZ     福建省          "\
"36  BENC     江西省          "\
"37  BEJN     山东省          "\
"41  BEZZ     河南省          "\
"42  BCWH     湖北省          "\
"43  BECS     湖南省 "\
"44  BCGZ     广东省 "\
"45  BENN     广西壮族自治区 "\
"46  BEHK     海南省 "\
"50  BECQ     重庆市 "\
"51  BCCD     四川省 "\
"52  BEGY     贵州省 "\
"53  BEKM     云南省 "\
"54  BELS     西藏自治区 "\
"61  BEXA     陕西省 "\
"62  BCLZ     甘肃省 "\
"63  BEXN     青海省 "\
"64  BEYC     宁夏回族自治区 "\
"65  BCUQ     新疆维吾尔自治区 "
'''

__mask_infos_with_mask = {11:["BEPK","北京市"],
                        12:["BETJ","天津市"],
                        13:["BESZ","河北省"],
                        14:["BETY","山西省"],
                        15:["BEHT","内蒙古自治区"],
                        21:["BCSY","辽宁省"],
                        22:["BECC","吉林省"],
                        23:["BEHB","黑龙江省"],
                        31:["BCSH","上海市"],
                        32:["BENJ","江苏省"],
                        33:["BEHZ","浙江省"],
                        34:["BEHF","安徽省"],
                        35:["BEFZ","福建省"],
                        36:["BENC","江西省"],
                        37:["BEJN","山东省"],
                        41:["BEZZ","河南省"],
                        42:["BCWH","湖北省"],
                        43:["BECS","湖南省"],
                        44:["BCGZ","广东省"],
                        45:["BENN","广西壮族自治区"],
                        46:["BEHK","海南省"],
                        50:["BECQ","重庆市"],
                        51:["BCCD","四川省"],
                        52:["BEGY","贵州省"],
                        53:["BEKM","云南省"],
                        54:["BELS","西藏自治区"],
                        61:["BEXA","陕西省"],
                        62:["BCLZ","甘肃省"],
                        63:["BEXN","青海省"],
                        64:["BEYC","宁夏回族自治区"],
                        65:["BCUQ","新疆维吾尔自治区"]}

__mask_infos_with_code = {"BEPK":[11,"北京市"],
                        "BETJ":[12,"天津市"],
                        "BESZ":[13,"河北省"],
                        "BETY":[14,"山西省"],
                        "BEHT":[15,"内蒙古自治区"],
                        "BCSY":[21,"辽宁省"],
                        "BECC":[22,"吉林省"],
                        "BEHB":[23,"黑龙江省"],
                        "BCSH":[31,"上海市"],
                        "BENJ":[32,"江苏省"],
                        "BEHZ":[33,"浙江省"],
                        "BEHF":[34,"安徽省"],
                        "BEFZ":[35,"福建省"],
                        "BENC":[36,"江西省"],
                        "BEJN":[37,"山东省"],
                        "BEZZ":[41,"河南省"],
                        "BCWH":[42,"湖北省"],
                        "BECS":[43,"湖南省"],
                        "BCGZ":[44,"广东省"],
                        "BENN":[45,"广西壮族自治区"],
                        "BEHK":[46,"海南省"],
                        "BECQ":[50,"重庆市"],
                        "BCCD":[51,"四川省"],
                        "BEGY":[52,"贵州省"],
                        "BEKM":[53,"云南省"],
                        "BELS":[54,"西藏自治区"],
                        "BEXA":[61,"陕西省"],
                        "BCLZ":[62,"甘肃省"],
                        "BEXN":[63,"青海省"],
                        "BEYC":[64,"宁夏回族自治区"],
                        "BCUQ":[65,"新疆维吾尔自治区"]}

def get_mask_infos_with_mask():
    return __mask_infos_with_mask

def get_mask_infos_with_code():
    return __mask_infos_with_code

def find_mask_with_code(mask):
    try:
        return __mask_infos_with_mask[mask]
    except:
        return None

def find_code_with_mask(code):
    try:
        return __mask_infos_with_code[code]
    except:
        return None


if __name__ == '__main__':
    #print(a)
    print('test done')


