#!/usr/bin/python
# -*- coding: utf-8 -*-
#Filename: loglibmul.py

'''
Created on May 14, 2021

@author: anduin
'''

import logging
import logging.handlers

class LogLibMul:
    '''
    日志格式‘%(asctime)s %(levelname)s %(module)s %(lineno)d %(message)s’
    
    使用TimedRotatingFileHandler时，保持240个日志备份，每小时一个日志文件。
    使用ConcurrentRotatingFileHandler时，保持100个1MB的文件。
    上面两个handle仅使用一个。
    
    使用前调用init初始化
    使用LogLibMul.loggers中logger对象的debug、info、warn、error、critical写日志
    系统结束后调用unint
    '''

    def __init__(self):
        self.loggers = {}
        
        self.lhandles = {}

    def __del__(self):
        self.uninit()

    def init(self, names):
        try:
            for name in set(names):
                logger = logging.getLogger(name)

                self.loggers[name] = logger

            return True
        except Exception as data:
            print('LogLib init exception:%s' % (str(data)))
            return False
    
    def addTimedRotatingFileHandler(self, filenames):
        try:
            for name, filename in filenames.items():
                if name not in self.loggers:
                    return False

                if name in self.lhandles:
                    return False

                if __name__ == '__main__':
                    #for test
                    lhandle = logging.handlers.TimedRotatingFileHandler(filename, 'm', 1, 3)
                else:
                    lhandle = logging.handlers.TimedRotatingFileHandler(filename, 'h', 1, 240)
                
                formatter = logging.Formatter('%(asctime)s %(levelname)s %(module)s %(lineno)d %(message)s')
                lhandle.setFormatter(formatter)

                self.loggers[name].addHandler(lhandle)
                self.lhandles[name] = lhandle

            return True
        except Exception as data:
            print('LogLib addTimedRotatingFileHandler exception:%s' % (str(data)))
            return False
        
    def setLevel(self, levels):
        try:
            for name, level in levels.items():
                if name not in self.loggers:
                    return False

                self.loggers[name].setLevel(level)

            return True
        except Exception as data:
            print('LogLib setLevel exception:%s' % (str(data)))
            return False
        
    def getlogger(self, name):
        return self.loggers[name]

    def uninit(self):
        """
        清理
        """
        for name, lhandle in self.lhandles.items():
            try:
                lhandle.flush()
            except Exception as f_data:
                print('LogLib uninit flush error %s %s' % (name, str(f_data)))

            try:
                lhandle.close()
            except Exception as c_data:
                print('LogLib uninit close error %s %s' % (name, str(c_data)))

            try:
                self.loggers[name].removeHandler(lhandle)
            except Exception as r_data:
                print('LogLib uninit remove handle error %s %s' % (name, str(r_data)))
        
        self.lhandles.clear()

        self.loggers.clear()
        
#for test
if __name__ == '__main__':
    import time

    loglib = LogLibMul()

    loglib.init(['a', 'b', 'c'])

    print(loglib.loggers['a'].hasHandlers())

    loglib.addTimedRotatingFileHandler({'a':'./a.log', 'b':'./b.log', 'c':'./c.log'})
    
    print(loglib.loggers['a'].hasHandlers())

    for i in range(0, 5):
        loglib.getlogger('a').error('abc')

    for i in range(0,5):
        loglib.getlogger('c').error('abc')
        
    loglib.uninit()
    
    print('test done')
    
