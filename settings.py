# conding:utf-8
import os
BASE_DIR = os.path.dirname(__file__)
redis_options = {
    'redis_host': '127.0.0.1',
    'redis_port': 6379,
    'redis_pass': '',
}
mongodb_options = {
    'alias': 'default',
    'db': 'tornademo',
    'host': '127.0.0.1',
    'port': 27017,
    # 'username': 'username',
    # 'password': 'password',
    # 'authentication_source': 'authentication_source',
    # 'authentication_mechanism': 'authentication_mechanism',
}


web = {
    'template_path': os.path.join(BASE_DIR, 'templates'),
    'static_path': os.path.join(BASE_DIR, 'static'),
    'media_path': os.path.join(BASE_DIR, 'media'),
    'cookie_secret': 'justforfun',
    'xsrf_cookies': False,
    'login_url': '/login',
    'debug': True,
}

log_path = os.path.join(BASE_DIR, 'data/logs/app.log')
use_template = True
LOGIN_URL = '/login'

ui = {
    'site_title': 'Tornado Demo Site',
    'title_sep': ' - ',
}
try:
    from local_settings import *  # noqa
except:
    pass
