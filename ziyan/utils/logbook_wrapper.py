# encoding: utf-8

import sys

from logbook import StreamHandler, RotatingFileHandler
from logbook import set_datetime_format

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
    :param conf:  toml[logging]
    :return: None
    """
    str_output = conf['str_output']  # console output
    str_level = conf['str_level']  # choose console log level to print
    log_output = conf['log_output']  # local log file output
    log_level = conf['log_level']  # choose log file level to save
    logfile = conf['log_file']  # local log file save position
    backup_count = conf['backup_count']  # count of local log files
    max_size = conf['max_size']  # size of each local log file
    format_string = conf['format_string']  # log message format
    # open console print
    if str_output is True:
        StreamHandler(sys.stdout, level=str_level, format_string=format_string, bubble=True).push_application()
    # open local log file output
    if log_output is True:
        RotatingFileHandler(logfile, mode='a', encoding='utf-8', level=log_level,
                            format_string=format_string, delay=False, max_size=max_size,
                            backup_count=backup_count, filter=None, bubble=True
                            ).push_application()

    return None


if __name__ == '__main__':
    from ziyan.utils.util import get_conf
    from logbook import Logger

    conf = get_conf('../text_file/configuration.toml')['log_configuration']
    setup_logger(conf)
    log = Logger('test')
    log.debug(conf)
    log.debug('debug:test')
    log.info('info:test')
    log.notice('notice:test')
    log.warn('warning:test')
    log.error('error:test')
    log.critical('critical:test')
