#! /usr/bin/env python
# -*- coding: utf-8 -*-
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired, BadTimeSignature
from . import db, login_manager
from flask import current_app
from datetime import datetime


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    auth_level = db.Column(db.Integer, nullable=False, default=0)

    instances = db.relationship('Instance', backref='user', lazy='dynamic')

    # 以下函数分别用于对用户密码进行读取保护、散列化以及验证密码
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # 以下两个函数用于token的生成和校验
    def generate_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired as e:
            # raise e
            return None
        except BadTimeSignature as e:
            # raise e
            return None
        uid = data.get('id')
        if uid:
            return User.query.get(uid)
        return None


# 插件flask_login的回调函数，用于读取用户


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class Instance(db.Model):
    __tablename__ = 'instance'
    id = db.Column(db.Integer, primary_key=True)  # 实例id
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'))  # 所属应用ID
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # 所属用户ID
    instance_name = db.Column(db.String(128), nullable=False)  # 实例名称
    cpu_num = db.Column(db.Integer)  # 消耗cpu（千分之一核）
    memory_num = db.Column(db.Integer)  # 消耗内存（M）
    container_num = db.Column(db.Integer, default=1)  # 消耗容器数（个），默认为1
    created_time = db.Column(db.DateTime(), default=datetime.now())  # 实例创建时间
    status = db.Column(db.Integer, default=0)  # 1表示实例暂停，0表示实例运行， 2表示正在创建


class Image(db.Model):
    __tablename__ = 'image'
    id = db.Column(db.Integer, primary_key=True)                # 镜像id
    image = db.Column(db.String(128), nullable=False)           # 创建镜像时实际用的名称
    image_name = db.Column(db.String(128), nullable=False)      # 镜像名称

    instances = db.relationship('Instance', backref='image', lazy='dynamic')




