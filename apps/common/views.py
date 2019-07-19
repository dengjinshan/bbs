#coding:utf-8
from flask import Blueprint, request, make_response, current_app
from io import BytesIO

from redis import RedisError

from utils.aliyunsdk.aliyunsms import send_sms
from utils import restful
from utils.captcha import Captcha
from apps.front.forms import SMSCaptchaForm
from tasks import send_sms_captcha


# 创建蓝图实例
bp = Blueprint('common', __name__, url_prefix='/common')

@bp.route('/')
def index():
    return 'common index'


@bp.route('/captcha/')
def graph_captcha():
    # 获取图形验证码
    text, image = Captcha.gene_graph_captcha()
    try:
        se = current_app.redis
        se.setex('image_code', 60 * 5, text)
    except RedisError as e:
        print(e)
        return 'redis问题'
    # bytest 字节流
    out = BytesIO()  # 图片转成二进制再发送发给浏览器显示
    image.save(out, 'png')  # 图片保存对象和类型
    out.seek(0)  # 将文件指针移动到文件首，保存后指针位于末尾
    resp = make_response(out.read())  # 将数据读取后添加到response返回
    resp.content_type = 'image/png'  # 指定文件类型
    return resp


# @bp.route('/sms_captcha/')
# def sms_captcha():
#     # 发送短信验证码   版本安全性低
#     telephone = request.args.get('telephone')
#     if not telephone:
#         return restful.params_error(message='请输入手机号')
#
#     captcha = Captcha.gene_text(number=4)
#     if send_sms(telephone, captcha):
#         return restful.success()
#     else:
#         return restful.params_error(message='短信验证码发送失败')

@bp.route('/sms_captcha/', methods=['POST'])
def sms_captcha():
    form = SMSCaptchaForm(request.form)
    if form.validate():
        telephone = form.telephone.data
        captcha = Captcha.gene_text(number=4)

        try:
            se = current_app.redis
            se.setex('sms_code:%s' % telephone, 60 * 5, captcha)
        except RedisError as e:
            print(e)
            return 'redis问题'

        # if send_sms(telephone, captcha):
        #     return restful.success()
        # else:
        #     return restful.params_error(message='短信验证码发送失败')
        send_sms_captcha(telephone, captcha)
        return restful.success()
    else:
        return restful.params_error(message='参数错误')