#coding:utf-8
from functools import wraps
from flask import session, redirect, url_for, g
import config


def login_required(func):
    # 验证登陆
    @wraps(func)
    def inner(*args, **kwargs):
        if config.CMS_UESR_ID in session:
            return func(*args, **kwargs)
        else:
            return redirect(url_for('cms.login'))
    return inner


# 接收参数的装饰器，两层，外层接收参数后将参数返回执行内层，
# 内层就受参数后验证通过才真正执行被装饰函数
def permission_required(permission):
    # 验证用户权限
    def outter(func):
        @wraps(func)
        def inner(*args, **kwargs):
            user = g.cms_user
            if user.has_permission(permission):
                return func(*args, **kwargs)
            else:
                return redirect(url_for('cms.index'))
        return inner
    return outter