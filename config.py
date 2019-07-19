import os

import redis

SECRET_KEY = os.urandom(24)  # 指定密钥
DEBUG = True
ALLOWED_HOSTS = ['106.12.52.122']

HOSTNAME = '127.0.0.1'
PORT = '3306'
DATABASE = 'bbs'
USERNAME = 'root'
PASSWORD = 'mysql'

# 创建链接语句
DB_URL = "mysql+pymysql://{username}:{password}@{host}:{port}/{db}?charset=utf8".format(
    username=USERNAME,password=PASSWORD,host=HOSTNAME,port=PORT,db=DATABASE
)

SQLALCHEMY_DATABASE_URI = DB_URL
SQLALCHEMY_TRACK_MODIFICATIONS = False

CMS_UESR_ID = 'SADASDAF'

# 发送邮件配置
# MAIL_USE_TLS：端口号587
# MAIL_USE_SSL：端口号465
# QQ邮箱不支持非加密方式发送邮件
# 发送者邮箱的服务器地址
MAIL_SERVER = "smtp.qq.com"
MAIL_PORT = '587'
MAIL_USE_TLS = True
# MAIL_USE_SSL
MAIL_USERNAME = "1570301135@qq.com"
# 邮箱发送邮件授权码
MAIL_PASSWORD = "whddtmwwvexbhfeb"
MAIL_DEFAULT_SENDER = "1570301135@qq.com"

# redis设置
REDIS_DB_URL = {
    'host': '127.0.0.1',
    'port': 6379,
    'password': '',
    'db': 0
}

FRONT_USER_ID = 'fasdfsfdfsfsd'

# UEditor编辑器配置
# UEDITOR_UPLOAD_PATH = os.path.join(os.path.dirname(__file__),'images')
UEDITOR_UPLOAD_TO_QINIU = True
UEDITOR_QINIU_ACCESS_KEY = "Xpcdj_aETnBqhEovBCdL4FziK1qWypQAEGBWSOy7"
UEDITOR_QINIU_SECRET_KEY = "frxljlK17GKI62Ee0_3X1gJh8AqBKj9e4vYYLFFj"
UEDITOR_QINIU_BUCKET_NAME = "djs_toutiao"
UEDITOR_QINIU_DOMAIN = "https://portal.qiniu.com/pu9ggkti6.bkt.clouddn.com"

# 每一页的帖子数量
PER_PAGE = 4

# celery配置
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'
CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'