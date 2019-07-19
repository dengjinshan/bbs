from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from bbs import create_app
from exts import db
from apps.cms import models as cms_models
from apps.cms.models import CMSPermission, CMSRole
from apps.front import models as front_models
from apps.models import BannerModel

FrontUser = front_models.FrontUser
CMSUser = cms_models.CMSUser

app = create_app()
manager = Manager(app)

Migrate(app, db)
manager.add_command('db', MigrateCommand)

@manager.option('-u', '--username', dest='username')
@manager.option('-p', '--password', dest='password')
@manager.option('-e', '--email', dest='email')
def create_cms_user(username, password, email):
    user = CMSUser(username=username, password=password, email=email)
    db.session.add(user)
    db.session.commit()
    print('添加成功')

@manager.option('-t', '--telephone', dest='telephone')
@manager.option('-u', '--username', dest='username')
@manager.option('-p', '--password', dest='password')
def create_front_user(telephone, username, password):
    user = FrontUser(telephone=telephone, username=username, password=password)
    db.session.add(user)
    db.session.commit()

@manager.command
def create_role():
    # 创建角色
    # 1,访问者（可以修改个人信息）
    visitor = CMSRole(name='访问者', desc='只能修改个人相关数据')
    visitor.permissions = CMSPermission.VISITOR

    # 2,运营角色（修改个人信息，管理帖子，管理评论，管理前台用户）
    operator = CMSRole(name='运营', desc='管理帖子，管理评论，管理前台用户')
    operator.permissions = CMSPermission.VISITOR|CMSPermission.POSTER|CMSPermission.CMSUSER\
                           |CMSPermission.COMMENTER|CMSPermission.FRONTUSER

    # 3,管理员（拥有绝大部分权限）
    admin = CMSRole(name='管理员', desc='拥有本系统所有权限')
    admin.permissions = CMSPermission.VISITOR|CMSPermission.POSTER|CMSPermission.CMSUSER\
                        |CMSPermission.COMMENTER|CMSPermission.FRONTUSER|CMSPermission.BOARDER

    # 4，开发者
    developer = CMSRole(name='开发者', desc='开发人员专用角色')
    developer.permissions = CMSPermission.ALL_PERMISSION
    # 添加到数据库
    db.session.add_all([visitor, operator, admin, developer])
    db.session.commit()

@manager.option('-e', '--email', dest='email')
@manager.option('-n', '--name', dest='name')
def add_user_to_role(email, name):
    user = CMSUser.query.filter_by(email=email).first()
    if user:
        role = CMSRole.query.filter_by(name=name).first()
        if role:
            role.users.append(user)
            db.session.commit()
            print('用户添加到角色{}成功'.format(role))
        else:
            print('没有该角色{}'.format(role))
    else:
        print('没有该用户{}'.format(email))

def test_permission():
    # 测试用户权限
    user = CMSUser.query.first()
    if user.is_developer:
        print('该用户没有访问者权限')
    else:
        print('用户有访问者权限')


if __name__ == '__main__':
    manager.run()