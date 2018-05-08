#! /usr/bin/env python
# -*- coding: utf-8 -*-

from flask import request, jsonify
from ..models import User
from functools import wraps


def admin_login(func):
    """过滤器：验证token是否为管理员"""
    @wraps(func)
    def wrap(*args, **kwargs):
        token = request.cookies.get('kubernetes_token')
        if token is None:
            return jsonify({'message': 'please login again'}), 400
        else:
            u = User.verify_token(token)
            if u and u.auth_level == 1:
                return func(*args, **kwargs)
            else:
                return jsonify({'message': 'you are not administrator'}), 400
    return wrap


def user_auth(func):
    """过滤器：检查用户token是否合法"""
    @wraps(func)
    def wrap(*args, **kwargs):
        token = request.cookies.get('kubernetes_token')
        if token is None:
            return jsonify({'message': 'please login again'}), 400
        else:
            u = User.verify_token(token)
            if u:
                return func(*args, **kwargs)
            else:
                return jsonify({'message': 'invalid identification,please login again'}), 400
    return wrap
