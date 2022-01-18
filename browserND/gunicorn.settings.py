import os
from os.path import join, exists

reload = False      # change it back to false before deploying

default_proc_name = 'gunicorn_browserND'

bind = '10.50.50.212:5080'

workers = 6

worker_class = 'gevent'

keyfile = join('cert','key.pem')

certfile = join('cert', 'cert.pem')

#logging

if not exists('logs'):
   os.mkdir('logs')

accesslog = join('logs', 'guni_access.log')
errorlog = join('logs', 'errors_log.log')

