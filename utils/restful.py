#coding:utf-8
from flask import jsonify

class HttpCode(object):
    # 定义错误状态码
    ok = 200
    unautherror = 401
    paramserror = 400
    servererror = 500

def restfult_result(code, message, data):
    # 定义提示信息
    return jsonify({'code':code, 'message':message, 'data':data})

# 分别定义提示信息
def success(message='', data=None):
    return restfult_result(code=HttpCode.ok, message=message, data=data)

def unauth_error(message=''):
    return restfult_result(code=HttpCode.unautherror, message=message, data=None)

def params_error(message=''):
    return restfult_result(code=HttpCode.paramserror, message=message, data=None)

def server_error(message=''):
    return restfult_result(code=HttpCode.servererror, message=message, data=None)