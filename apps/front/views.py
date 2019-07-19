from flask import Blueprint, views, render_template, make_response, request, session, redirect, url_for, g, abort
from sqlalchemy import func

from apps.front.forms import SignupForm, SigninForm, AddPostForm, AddCommentForm
from exts import db
from apps.front.models import FrontUser
from apps.models import BannerModel, BoardMode, PostModel, CommentModel, HightLishtPostModel
from flask_paginate import Pagination, get_page_parameter

from utils import safeutils
# 创建蓝图实例
from utils import restful
import config
from .decorators import login_required

bp = Blueprint('front', __name__)

# @bp.route('/')
# def index():
#     return 'front index'

@bp.route('/')
def index():
    board_id = request.args.get('bd', type=int, default=None)  # 板块id
    page = request.args.get(get_page_parameter(), type=int, default=1)  # 页数
    sort = request.args.get('st', type=int, default=1)  # 页面内容排序

    banners = BannerModel.query.order_by(BannerModel.priority.desc()).limit(4)
    boards = BoardMode.query.all()

    # 页面开始结束位置
    start = (page-1)*config.PER_PAGE
    end = start + config.PER_PAGE
    posts = None
    total = 0

    query_obj = None
    if sort == 1:
        query_obj = PostModel.query.order_by(PostModel.create_time.desc())
    elif sort == 2:
        # 按照加精时间排序,没有加精的按照默认排序
        query_obj = db.session.query(PostModel).outerjoin(HightLishtPostModel).order_by(
            HightLishtPostModel.create_time.desc(), PostModel.create_time.desc())
    elif sort == 3:
        # 按照点赞数排序
        query_obj = PostModel.query.order_by(PostModel.create_time.desc())
    elif sort == 4:
        # 按照评论数排序,没有评论的按照默认排序
        query_obj  = db.session.query(PostModel).outerjoin(CommentModel).group_by(
            PostModel.id).order_by(func.count(CommentModel.id).desc(), PostModel.create_time.desc())

    if board_id:
        query_obj = query_obj.filter(PostModel.board_id==board_id)
        posts = query_obj.slice(start, end)
        total = query_obj.count()
    else:
        posts = query_obj.slice(start, end)
        total = query_obj.count()
    # 分页
    pagination = Pagination(bs_version=3, page=page, total=total, outer_window=0, inner_window=1, record_name='users')
    context = {
        'banners': banners,
        'boards': boards,
        'posts': posts,
        'pagination': pagination,
        'current_board': board_id,
        'current_sort': sort
    }
    return render_template('front/front_index.html', **context)


@bp.route('/d/<post_id>/')
def post_detail(post_id):
    # 帖子详情
    post = PostModel.query.get(post_id)
    if not post:
        abort(404)
    return render_template('front/front_postdetail.html', post=post)


@bp.route('/acomment/', methods=['POST'])
@login_required
def add_comment():
    form = AddCommentForm(request.form)
    if form.validate():
        content = form.content.data
        post_id = form.post_id.data
        post = PostModel.query.get(post_id)
        if post:
            comment = CommentModel(content=content)
            comment.post = post
            comment.author = g.front_user
            db.session.add(comment)
            db.session.commit()
            return restful.success()
        else:
            return restful.params_error(message='没有这篇帖子')
    else:
        return restful.params_error(message=form.get_error())


@bp.route('/apost/', methods=['GET', 'POST'])
def apost():
    # 帖子管理
    if request.method == 'GET':
        boards = BoardMode.query.all()
        return render_template('front/front_apost.html', boards=boards)
    else:
        form = AddPostForm(request.form)
        if form.validate():
            title = form.title.data
            content = form.content.data
            board_id = form.board_id.data
            board = BoardMode.query.get(board_id)
            if not board:
                return restful.params_error(message='板块不存在')
            post = PostModel(title=title, content=content)
            post.board = board
            post.author = g.front_user
            db.session.add(post)
            db.session.commit()
            return restful.success()
        else:
            return restful.params_error(message=form.get_error())

class SignupView(views.MethodView):
    # 前台用户注册
    def get(self):
        return_to = request.referrer  # 获得上一个页面的地址
        # 验证地址安全， 地址存在，而且不等于页面地址而且安全验证通过
        if return_to and return_to != request.url and safeutils.is_safe_url(return_to):
            return render_template('front/front_signup.html', return_to=return_to)
        else:
            return render_template('front/front_signup.html')
    def post(self):
        form = SignupForm(request.form)
        if form.validate():
            telephone = form.telephone.data
            username = form.username.data
            password = form.password1.data
            user = FrontUser(telephone=telephone, username=username, password=password)
            db.session.add(user)
            db.session.commit()
            return restful.success()
        else:
            return restful.params_error(message=form.get_error())

class SigninView(views.MethodView):
    # 前台用户登陆
    def get(self):
        return_to = request.referrer
        if return_to and return_to != request.url and safeutils.is_safe_url(return_to):
            return render_template('front/front_signin.html', return_to=return_to)
        else:
            return render_template('front/front_signin.html')

    def post(self):
        form = SigninForm(request.form)
        if form.validate():
            telephone = form.telephone.data
            password = form.password.data
            remember = form.remember.data
            user = FrontUser.query.filter_by(telephone=telephone).first()
            if user and user.check_password(password):
                session[config.FRONT_USER_ID] = user.id
                if remember:
                    session.permanent = True
                return redirect(url_for('front.index'))
            else:
                return restful.params_error(message='手机号或密码错误')
        else:
            return restful.params_error(message=form.get_error())


bp.add_url_rule('/signin/', view_func=SigninView.as_view('signin'))
bp.add_url_rule('/signup/', view_func=SignupView.as_view('signup'))