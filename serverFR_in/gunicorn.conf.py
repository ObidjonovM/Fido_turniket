import os
from os.path import join, exists


default_proc_name = 'serverFR_in'

bind = "10.50.50.212:5075"

workers = 1

worker_class = 'gevent'

# logging
if not exists('logs'):
    os.mkdir('logs')

accesslog = join('logs','access.log')
errorlog = join('logs', 'error.log')
