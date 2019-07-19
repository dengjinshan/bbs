#coding:utf-8
from flask import current_app

from apps.forms import BaseForm
from wtforms import StringField, IntegerField
from wtforms.validators import regexp, InputRequired, Regexp, EqualTo, ValidationError
import hashlib


class SMSCaptchaForm(BaseForm):
    # 短信验证码，加密验证
    salt = 'dsafdauiyqorhqsafsdio'
    telephone = StringField(validators=[regexp(r'1[345789]\d{9}')])
    timestamp = StringField(validators=[regexp(r'\d{13}')])
    sign = StringField(validators=[InputRequired()])

    def validate(self):
        # 验证方法
        result = super(SMSCaptchaForm, self).validate()
        if not result:
            return False

        telephone = self.telephone.data
        timestamp = self.timestamp.data
        sign = self.sign.data

        # md5(timestamp+telephone+salt)
        # md5函数必须要传递bytes类型字符串
        sk = (timestamp+telephone+self.salt).encode('utf-8')
        # hashlib.md5(sk) 生成md5对象 .hexdigest()获取字符串内容
        sign2 = hashlib.md5(sk).hexdigest()
        if sign == sign2:
            return True
        else:
            return False


class SignupForm(BaseForm):
    telephone = StringField(validators=[Regexp(r'1[1345789]\d{9}', message='请输入正确格式手机号')])
    sms_captcha = StringField(validators=[Regexp(r'\w{4}', message='请输入正确格式短信验证码')])
    username = StringField(validators=[Regexp(r'.{2,20}', message='请输入正确格式用户名')])
    password1 = StringField(validators=[Regexp(r'[0-9a-zA-Z_.]{6,20}', message='请输入正确格式密码')])
    password2 = StringField(validators=[EqualTo('password1', message='两次密码不一致')])
    graph_captcha = StringField(validators=[Regexp(r'\w{4}', message='请输入正确格式图形验证码')])

    def validate_sms_captcha(self, field):
        sms_captcha = field.data
        telephone = self.telephone.data

        r = current_app.redis
        sms_captcha_old = r.get('sms_code:%s' % telephone).decode()
        if not sms_captcha_old or sms_captcha.lower() != sms_captcha_old.lower():
            raise ValidationError(message='短信验证码错误')

    def validate_graph_captcha(self, field):
        graph_captcha = field.data
        r = current_app.redis
        graph_captcha_old = r.get('image_code')

        if not graph_captcha_old and graph_captcha.lower() != graph_captcha_old.lower():
            raise ValidationError(message='图形验证码错误')


class SigninForm(BaseForm):
    telephone = StringField(validators=[Regexp(r'1[3-9]\d{9}', message='请输入正确格式手机号')])
    password = StringField(validators=[Regexp(r'\w{6,20}', message='请输入正确格式密码')])
    remember = StringField()

class AddPostForm(BaseForm):
    title = StringField(validators=[InputRequired(message='请输入标题')])
    content = StringField(validators=[InputRequired(message='请输入内容')])
    board_id = IntegerField(validators=[InputRequired(message='请输入板块id')])

class AddCommentForm(BaseForm):
    content = StringField(validators=[InputRequired(message='请输入评论内容')])
    post_id = IntegerField(validators=[InputRequired(message='请输入帖子id')])