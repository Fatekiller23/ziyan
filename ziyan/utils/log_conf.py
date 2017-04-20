# encoding: utf-8

import sys

from logbook import StreamHandler,RotatingFileHandler
from logbook import set_datetime_format
#from logbook.queues
#from logbook.ticketing

'''
show local time in log line timestamp 
parameter:
        local : datetime in local time zone
        utc   : datetime in UTC time zone
'''
set_datetime_format('local')


def setup_logger(conf):
    """
    setup logbook
    :param conf:  config [logging]
    :return: None
    """
    str_output = conf['str_output']
    str_level = conf['str_level']
    log_output = conf['log_output']
    log_level = conf['log_level']
    logfile = conf['log_file']
    backup_count = conf['backup_count']
    max_size = conf['max_size']
    format_string = conf['format_string']

    if str_output:
        StreamHandler(sys.stdout,level=str_level,format_string=format_string,bubble=True).push_application()

    if log_output:
        RotatingFileHandler(logfile,mode='a',encoding='utf-8',level=log_level,\
                            format_string=format_string,delay=False,max_size=max_size,\
                            backup_count=backup_count,filter=None,bubble=True
                            ).push_application()

    return None


if __name__ ==  '__main__':
    from ziyan.utils.util import get_conf
    from logbook import Logger
    conf = get_conf('../text_file/configuration.toml')['logging']
    setup_logger(conf)
    log = Logger('test')
    log.debug(conf)
    log.debug('debug:test')
    log.info('info:test')
    log.notice('notice:test')
    log.warn('warning:test')
    log.error('error:test')
    log.critical('critical:test')










