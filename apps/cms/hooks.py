#coding:utf-8
from flask import session, g

from apps.cms import bp
from .models import CMSUser, CMSPermission
import config

@bp.before_request
def before_request():
    # 请求钩子函数
    if config.CMS_UESR_ID in session:
        user_id = session.get(config.CMS_UESR_ID)
        user = CMSUser.query.get(user_id)
        if user:
            g.cms_user = user

@bp.context_processor
def cms_context_processor():
    # 上下文处理
    return {'CMSPermission': CMSPermission}