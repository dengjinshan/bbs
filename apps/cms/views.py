#coding:utf-8
import random
import string

from flask import Blueprint, render_template, views, session, redirect, url_for, request, g, jsonify, current_app
from redis import RedisError

from .forms import LoginForm, ResetpwdForm,ResetemailForm, AddbannerForm, UpdateBannerForm, AddBoardForm, UpdateBoardForm
from .models import CMSUser, CMSPermission
from ..models import BannerModel, BoardMode, PostModel, HightLishtPostModel
from .decorators import login_required, permission_required
import config
from exts import db, mail
from flask_mail import Message
from utils import restful
from tasks import send_mail


# 创建蓝图实例
bp = Blueprint('cms', __name__, url_prefix='/cms')

@bp.route('/')
@login_required
def index():
    return render_template('cms/cms_index.html')


@bp.route('/logout/')
@login_required
def logout():
    del session[config.CMS_UESR_ID]
    return redirect(url_for('cms.login'))

@bp.route('/profile/')
@login_required
def profile():
    return render_template('cms/cms_profile.html')


@bp.route('/banners/')
def banners():
    banners = BannerModel.query.order_by(BannerModel.priority.desc()).all()
    return render_template('cms/cms_banners.html', banners=banners)


@bp.route('/abanner/', methods=['POST'])
def abanner():
    form = AddbannerForm(request.form)
    if form.validate():
        name = form.name.data
        image_url = form.image_url.data
        link_url = form.link_url.data
        priority = form.priority.data
        banner = BannerModel(name=name, image_url=image_url, link_url=link_url, priority=priority)
        db.session.add(banner)
        db.session.commit()
        return restful.success()
    else:
        return restful.params_error(message=form.get_error())


@bp.route('/ubanner/', methods=['POST'])
@login_required
def ubanner():
    form = UpdateBannerForm(request.form)
    if form.validate():
        banner_id = form.banner_id.data
        name = form.name.data
        image_url = form.image_url.data
        link_url = form.link_url.data
        priority = form.priority.data
        banner = BannerModel.query.get(banner_id)
        if banner:
            banner.name = name
            banner.image_url = image_url
            banner.link_url = link_url
            banner.priority = priority
            db.session.add(banner)
            db.session.commit()
            return restful.success()
        else:
            return restful.params_error(message='banner不存在')
    else:
        return restful.params_error(message=form.get_error())


@bp.route('/dbanner/', methods=['POST'])
@login_required
def dbanner():
    banner_id = request.form.get('banner_id')
    if not banner_id:
        return restful.params_error(message='请传入轮播图id')
    banner = BannerModel.query.get(banner_id)
    if not banner:
        return restful.params_error(message='没有这个轮播图')
    db.session.delete(banner)
    db.session.commit()
    return restful.success()


@bp.route('/email_captcha/')
def email_captcha():
    email = request.args.get('email')
    if not email:
        return restful.params_error('请输入邮箱')

    source = list(string.ascii_letters)  # 获取26个字母列表
    source.extend(map(lambda x:str(x), range(0,10)))  # 生成0-9数字，并将其转成字符串，插入字母中
    captcha = ''.join(random.sample(source, 6))  # 从列表中随机取出6个字符，并将其合并成完整的字符串
    # 发送邮件内容
    # message = Message('论坛验证码', recipients=[email], body='您的验证码是：%s'%captcha)
    # try:
    #     mail.send(message)
    # except Exception as e:
    #     return restful.server_error('内部异常')
    send_mail.delay('论坛验证码', [email], '您的验证码是：%s'%captcha)
    # 将验证码存在redis中
    try:
        se = current_app.redis
        se.setex('email', 60 * 5, captcha)
    except RedisError as e:
        print(e)
        return 'redis问题'
    return restful.success()


# @bp.route('/email/')
# def send_mail():
#     message = Message('邮件发送', recipients=['1570301135@qq.com'], body='测试')
#     mail.send(message)
#     return 'success'


@bp.route('/posts/')
@login_required
@permission_required(CMSPermission.POSTER)
def posts():
    post_list = PostModel.query.all()
    return render_template('cms/cms_posts.html', posts=post_list)


@bp.route('/hposts/', methods=['POST'])
@login_required
@permission_required(CMSPermission.POSTER)
def hpost():
    post_id = request.form.get('post_id')
    if not post_id:
        return restful.params_error('请输入帖子id')
    post = PostModel.query.get(post_id)
    if not post:
        return restful.params_error('没有当前帖子')
    highlight = HightLishtPostModel()
    highlight.post = post
    db.session.add(highlight)
    db.session.commit()
    return restful.success()


@bp.route('/uhposts/', methods=['POST'])
@login_required
@permission_required(CMSPermission.POSTER)
def uhpost():
    post_id = request.form.get('post_id')
    if not post_id:
        return restful.params_error('请输入帖子id')
    post = PostModel.query.get(post_id)
    if not post:
        return restful.params_error('没有当前帖子')
    highlight = HightLishtPostModel.query.filter_by(post_id=post_id).first()
    db.session.delete(highlight)
    db.session.commit()
    return restful.success()


@bp.route('/comments/')
@login_required
@permission_required(CMSPermission.COMMENTER)
def comments():
    return render_template('cms/cms_comments.html')


@bp.route('/boards/')
@login_required
@permission_required(CMSPermission.BOARDER)
def boards():
    # 展示板块
    board_models = BoardMode.query.all()
    context = {
        'boards': board_models
    }
    return render_template('cms/cms_boards.html', **context)


@bp.route('/aboard/', methods=['POST'])
@login_required
@permission_required(CMSPermission.BOARDER)
def aboard():
    # 创建板块
    form = AddBoardForm(request.form)
    if form.validate():
        name = form.name.data
        board = BoardMode(name=name)
        db.session.add(board)
        db.session.commit()
        return restful.success()
    else:
        return restful.params_error(message=form.get_error())


@bp.route('/uboard/', methods=['POST'])
@login_required
@permission_required(CMSPermission.BOARDER)
def uboard():
    # 修改板块
    form = UpdateBoardForm(request.form)
    if form.validate():
        board_id = form.board_id.data
        name = form.name.data
        board = BoardMode.query.get(board_id)
        if board:
            board.name = name
            db.session.commit()
            return restful.success()
        else:
            return restful.params_error(message='没有该板块id')
    else:
        return restful.params_error(message=form.get_error())


@bp.route('/dboard/', methods=['POST'])
@login_required
@permission_required(CMSPermission.BOARDER)
def dboard():
    # 删除板块
    board_id = request.form.get('board_id')
    if not board_id:
        return restful.params_error('请输入模板id')
    board = BoardMode.query.get(board_id)
    if not board:
        return restful.params_error(message='没有这个板块')
    db.session.delete(board)
    db.session.commit()
    return restful.success()


@bp.route('/fusers/')
@login_required
@permission_required(CMSPermission.FRONTUSER)
def fusers():
    return render_template('cms/cms_fusers.html')


@bp.route('/cusers/')
@login_required
@permission_required(CMSPermission.CMSUSER)
def cusers():
    return render_template('cms/cms_cursers.html')


@bp.route('/croles/')
@login_required
@permission_required(CMSPermission.ALL_PERMISSION)
def croles():
    return render_template('cms/cms_croles.html')


# 登陆
class LoginView(views.MethodView):

    def get(self, message=None):
        return render_template('cms/cms_login.html', message=message)

    def post(self):
        form = LoginForm(request.form)
        if form.validate():
            email = form.email.data
            password = form.password.data
            remember = form.remember.data
            user = CMSUser.query.filter_by(email=email).first()

            if user and user.check_password(password):
            # if user:
                session[config.CMS_UESR_ID] = user.id
                if remember:
                    session.permanent = True
                return redirect(url_for('cms.index'))
            else:
                return self.get(message='邮箱密码错误')
        else:
            message = form.get_error()
            return self.get(message=message)


# 修改密码
class ResetPwdView(views.MethodView):
    decorators = [login_required]
    def get(self):
        return render_template('cms/cms_resetpwd.html')

    def post(self):
        form = ResetpwdForm(request.form)
        if form.validate():
            oldpwd = form.oldpwd.data
            newpwd = form.newpwd.data
            user = g.cms_user
            if user.check_password(oldpwd):
                user.password = newpwd
                db.session.commit()
                # 调用定义好的提示方法
                return restful.success()
            else:
                return restful.params_error('旧密码错误')
        else:
            message = form.get_error()
            return restful.params_error(message)

# 修改邮箱
class ResetEmailView(views.MethodView):
    decorators = [login_required]
    def get(self):
        return render_template('cms/cms_resetemail.html')

    def post(self):
        form = ResetemailForm(request.form)
        if form.validate():
            email = form.email.data
            g.cms_user.email = email
            db.session.commit()
            return restful.success()
        else:
            return restful.params_error(form.get_error())

bp.add_url_rule('/login/', view_func=LoginView.as_view('login'))
bp.add_url_rule('/resetpwd/', view_func=ResetPwdView.as_view('resetpwd'))
bp.add_url_rule('/resetemail/', view_func=ResetEmailView.as_view('resetemail'))