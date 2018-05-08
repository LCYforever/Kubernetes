#! /usr/bin/env python
# -*- coding: utf-8 -*-
from . import user
from ..models import User
from flask import request, jsonify, make_response
from ..util.authorize import admin_login
from .. import db
import json


"""
    用户注册，只有前端管理员才能进行此操作
"""


@user.route('/reg', methods=['GET', 'POST'])
@admin_login
def reg():
    if request.method == 'GET':
        message_e = 'only post method is supported'
        return message_e, 404
    else:
        data = request.get_data()
        json_data = json.loads(data)
        username = json_data['username']
        password = json_data['password']
        if User.query.filter_by(username=username).first():
            message_e = 'The user has been already authorized'
            return jsonify({'message': message_e}), 400
        else:
            u = User()
            u.username = username
            u.password = password
            u.auth_level = 0
            db.session.add(u)
            db.session.commit()
            message_e = 'authorize success'
            return jsonify({'message': message_e})


"""
    用户登录获取token
"""


@user.route('/auth', methods=['GET', 'POST'])
def auth():
    if request.method == 'GET':
        message_e = 'only post method is supported'
        return jsonify({'message': message_e})
    else:
        data = request.get_data()
        json_data = json.loads(data)
        username = json_data['username']
        password = json_data['password']
        u = User.query.filter_by(username=username).first()
        if u is None:
            message_e = 'user is not exist'
            return jsonify({'message': message_e}), 404
        if not u.verify_password(password):
            message_e = 'password incorrect'
            return jsonify({'message': message_e}), 400
        else:
            return_data = {'id': u.id, 'username': username}
            rsp = make_response(jsonify(return_data))
            rsp.set_cookie('kubernetes_token', u.generate_token())
            return rsp


