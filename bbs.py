#coding:utf-8
import redis
from flask import Flask, Session
from apps.cms import bp as cms_bp
from apps.common import bp as common_bp
from apps.front import bp as front_bp
from apps.ueditor import bp as ueditor_bp
import config
from exts import db, mail
from flask_wtf import CSRFProtect


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)
    # 注册蓝图
    app.register_blueprint(cms_bp)
    app.register_blueprint(common_bp)
    app.register_blueprint(front_bp)
    app.register_blueprint(ueditor_bp)

    db.init_app(app)
    mail.init_app(app)  # 初始化发送app
    # 注册redis
    app.redis = redis.Redis(**config.REDIS_DB_URL)
    CSRFProtect(app) # csrf防护
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(port=8000)