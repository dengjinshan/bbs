from flask import g, current_app
from wtforms import Form, StringField, IntegerField
from wtforms.validators import Email, InputRequired, Length, EqualTo, ValidationError
from apps.forms import BaseForm


class LoginForm(BaseForm):
    # 登陆验证表单
    email = StringField(validators=[Email(message='邮箱格式不正确'), InputRequired(message='请输入邮箱')])
    password = StringField(validators=[Length(6, 20, message='密码不正确')])
    remember = IntegerField()


class ResetpwdForm(BaseForm):
    # 修改密码验证表单
    oldpwd = StringField(validators=[Length(6, 20, message='旧密码格式不正确')])
    newpwd = StringField(validators=[Length(6, 20, message='新密码格式不正确')])
    newpwd2 = StringField(validators=[EqualTo('newpwd', message='两次密码不一致')])


class ResetemailForm(BaseForm):
    # 修改邮箱验证表单
    email = StringField(validators=[Email(message='请输入正确邮箱')])
    captcha = StringField(validators=[Length(max=6, min=6, message='验证码长度不正确')])

    def validate_captcha(self, field):
        captcha = field.data  # 获取用户输入验证码
        email = self.email.data  # 获取当前用户邮箱
        # 连接redis
        se = current_app.redis
        captcha_cache = se.get('email').decode()  # 获取缓存中验证码
        # 这里获取验证码后应该删除缓存
        # se.delete('email')
        if not captcha_cache or captcha_cache.lower() != captcha.lower():
            raise ValidationError('邮箱验证码错误')

    def validate_email(self, field):
        email = field.data  # 输入邮箱
        user = g.cms_user  # 当前用户
        if user.email == email:
            raise ValidationError('不能修改为相同的邮箱')


class AddbannerForm(BaseForm):
    # 轮播图添加验证
    name = StringField(validators=[InputRequired(message='请输入轮播图名称')])
    image_url = StringField(validators=[InputRequired(message='请输入轮播图图片链接')])
    link_url = StringField(validators=[InputRequired(message='请输入轮播图跳转链接')])
    priority = IntegerField(validators=[InputRequired(message='请输入轮播图权重')])

class UpdateBannerForm(AddbannerForm):
    banner_id = IntegerField(validators=[InputRequired(message='请输入轮播图id')])


class AddBoardForm(BaseForm):
    name = StringField(validators=[InputRequired(message='请输入板块名称')])

class UpdateBoardForm(AddBoardForm):
    board_id = IntegerField(validators=[InputRequired(message='请输入板块id')])