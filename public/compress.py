#!/usr/bin/python
# -*- coding: utf-8 -*-
#Filename: compress.py

'''
Created on Jan 26, 2021

@author: anduin
'''

import os
import zipfile
import tarfile

def __get_zip_file(input_path, base_name, result):
    """
    对目录进行深度优先遍历
    :param input_path:
    :param base_name
    :param result:
    :return:
    """

    files = os.listdir(input_path)
    for file in files:
        fullpath = os.path.join(input_path, file)
        cur_base_name = file if len(base_name) == 0 else base_name + '/' + file
        if os.path.isdir(fullpath):
            __get_zip_file(fullpath, cur_base_name, result)
        else:
            result.append([fullpath, cur_base_name])

def zip_file_path(input_path, output_path, compression=zipfile.ZIP_DEFLATED):
    """
    压缩文件
    :param input_path: 压缩的文件夹路径
    :param output_path: 解压（输出）的文件名
    :param compression:ZIP_STORED=0,(no compression),ZIP_DEFLATED=8,(requires zlib),ZIP_BZIP2=12,(requires bz2),ZIP_LZMA=14,(requires lzma)
    :return:
    """

    try:
        filelists = []
        if os.path.isfile(input_path):
            d,fn = os.path.split(input_path)
            filelists.append([input_path, fn])
        else:
            __get_zip_file(input_path, os.path.basename(input_path), filelists)

        with zipfile.ZipFile(output_path, 'w', compression) as f:
            for file in filelists:
                f.write(file[0], file[1])

        return True
    except Exception as data:
        return False


def tar_file_path(input_path, output_path, compression='bz2'):
    """
    压缩文件
    #input_path:dir or file name
    #output_path:file name
    #compression:gz:gzip or bz2:bzip2 or xz:lzma,空字符串是不压缩。
    """

    try:
        arc_name = ''
        if os.path.isdir(input_path):
            arc_name = os.path.basename(input_path)
        else:
            d,fn = os.path.split(input_path)
            arc_name = fn

        # 压缩方法决定了open的第二个参数是 "w", 或"w:gz", 或"w:bz2"
        if compression: 
            dest_cmp = ':' + compression 
        else: 
            dest_cmp = ''

        with tarfile.TarFile.open(output_path, 'w' + dest_cmp) as out:
            out.add(input_path, arcname=arc_name)

        return True
    except Exception as data:
        return False

if __name__ == '__main__':
    #zip_file_path(r"C:\testdata\Caiyun_pd\Caiyun_h5", r'C:\testdata\Caiyun_pd\Caiyun_h5\123.zip')
    #zip_file_path(r"C:\testdata\Caiyun_pd\Caiyun_h5\BT202010280200.h5", r'C:\testdata\Caiyun_pd\Caiyun_h5\BT202010280200.h5.zip')

    #tar_file_path(r"C:\testdata\Caiyun_pd\Caiyun_h5", r'C:\testdata\Caiyun_pd\Caiyun_h5\123.tar.gz')
    #tar_file_path(r"C:\testdata\Caiyun_pd\Caiyun_h5\BT202010280200.h5", r'C:\testdata\Caiyun_pd\Caiyun_h5\BT202010280200.h5.tar.gz')

    print('test done')


