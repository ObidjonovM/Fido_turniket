import os
from os.path import join, exists

default_proc_name = 'serverFR_out'

bind = "10.50.50.212:5076"

workers = 1

worker_class = 'gevent'

# logging
if not exists('logs'):
    os.mkdir('logs')

accesslog = join('logs', 'access.log')
errorlog = join('logs', 'error.log')

# cmd to start (ONLY FOR THIS CASE!!!) : gunicorn 'run_server:start_app()' -c gunicorn.conf.py