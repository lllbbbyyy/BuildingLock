#models.py

import sys
import jwt

sys.path.append("..")
from db_manage.sql import db

import config.config as config
from config.config import Config

#在此处定义数据库类型对象
"""
一对一关系中，需要设置relationship中的uselist=Flase，其他数据库操作一样。
一对多关系中，外键设置在多的一方中，关系（relationship）可设置在任意一方。
多对多关系中，需建立关系表，设置 secondary=关系表
"""


class User(db.Model):
    #主键为id
    id = db.Column(db.Integer, primary_key=True)
    #不允许相同值
    openid = db.Column(db.String(120), unique=True)
    session_key = db.Column(db.String(120))
    uuid = db.Column(db.String(120), unique=True)
    username = db.Column(db.String(120))
    phonenum = db.Column(db.String(120))


class Lock(db.Model):
    #主键为id
    id = db.Column(db.Integer, primary_key=True)
    #锁体名称
    lockname = db.Column(db.String(120))
    #锁体的用户uuid
    lockmasteruuid = db.Column(db.String(120))
    #功能模块是否存在
    qrcode = db.Column(db.String(120))
    monitor = db.Column(db.String(120))
    password = db.Column(db.String(120))
    nfc = db.Column(db.String(120))
    alart = db.Column(db.String(120))
    logic = db.Column(db.String(300))
