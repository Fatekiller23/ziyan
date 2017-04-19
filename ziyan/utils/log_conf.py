# encoding: utf-8

import os
import sys

from logbook import StreamHandler,RotatingFileHandler
from logbook import set_datetime_format

'''
show local time in log line timestamp 
parameter:
        local : datetime in local time zone
        utc   : datetime in UTC time zone
'''
set_datetime_format('local')


def setup_logger(conf):
    '''
    setup logbook
    :param conf:  config 
    :return: None
    '''
    str_output = conf['str_output']
    str_level = conf['str_level']
    log_output = conf['log_output']
    log_level = conf['log_level']
    logfile = conf['log_file']
    backup_count = conf['backup_count']
    max_size = conf['max_size']
    format_string = conf['format_string']

    if str_output:
        StreamHandler(sys.stdout,level=str_level,format_string=format_string).push_application()

    elif log_output:
        RotatingFileHandler(logfile,mode='a',encoding='utf-8',level=log_level,\
                            format_string=format_string,delay=False,max_size=max_size,\
                            backup_count=backup_count,filter=None,bubble=True
                            ).push_application()

    return None










