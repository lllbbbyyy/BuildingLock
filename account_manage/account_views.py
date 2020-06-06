#account_views.py
#账户视图模块
#系统导入
from functools import wraps
from sqlalchemy import and_, or_
from flask import request, render_template, redirect, url_for, flash, session, Blueprint, jsonify
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename
import os
#import cv2
import time
import sys
import datetime
import random
import json, requests
import uuid
import jwt

from selenium import webdriver
#
sys.path.append("..")
from db_manage.sql import db
from config.config import appID, appSecret, Config
from account_manage.account_models import User,Lock

#跨文件路由需要蓝图
account_app = Blueprint('user', __name__)

##辅助函数
def login():
    code = request.values.get('code')
    code = json.loads(code)
    req_params = {
        'appid': appID,
        'secret': appSecret,
        'js_code': code,
        'grant_type': 'authorization_code'
    }
    wx_login_api = 'https://api.weixin.qq.com/sns/jscode2session'
    response_data = requests.get(wx_login_api, params=req_params)  #向API发起GET请求
    data = response_data.json()
    openid = data['openid']  #得到用户关于当前小程序的OpenID
    session_key = data['session_key']  #得到用户关于当前小程序的会话密钥session_key
    '''
	下面部分是通过判断数据库中用户是否存在来确定添加或返回自定义登录态（若用户不存在则添加；若用户存在，我这里返回的是添加用户时生成的自增长字段UserID）
	'''
    if openid and session_key:
        '''
    	在数据库用户表查询（查找得到的OpenID在数据库中是否存在）
    	SQLalchemy语句：
        '''
        user_info = User.query.filter(User.openid == openid).first()
        if user_info is None:  #不存在
            '''
	        将得到的OpenID添加到数据库得用户表
	        SQLalchemy语句：
            '''
            user_info = User(openid=openid,
                             session_key=session_key,
                             uuid=str(uuid.uuid1()),
                             username="",
                             phonenum="")
            db.session.add(user_info)
            db.session.commit()

        # token_dict = {
        #     #时间戳
        #     'iat': time.time(),
        #     #标识符
        #     'uuid': user_info.uuid
        # }
        # headers = {
        #     #使用的算法
        #     'alg': 'HS256'
        # }
        # jwt_token = jwt.encode(
        #     token_dict,  #有效载体
        #     Config.SECRET_KEY,  #加密密钥
        #     algorithm='HS256',  #加密算法
        #     headers=headers).decode('UTF-8')
        return_info={"userID":user_info.uuid}
        return json.dumps(return_info)  #将内容返回
    return "code失效或不正确"

def register():
    userid = request.values.get('userID')
    
    username = request.values.get('username')
    
    phonenum = request.values.get('phonenum')
    if userid is None or username is None or phonenum is None:
        return json.dumps({"state":"0"})
    userid = json.loads(userid)
    username = json.loads(username)
    phonenum = json.loads(phonenum)
    user = User.query.filter(User.uuid == userid).first()
    if user is None:
        return json.dumps({"state":"0"})
    user.username=username
    user.phonenum=phonenum
    db.session.commit()
    return json.dumps({"state":"1"})

#辅助函数
def get_lock_dict(all_lock_list):
    lock_list=[]
    for it in all_lock_list:
        lock={}
        lock["lockID"]=it.lockid
        lock["lockName"]=it.lockname
        lock["QRcode"]=it.qrcode
        lock["monitor"]=it.monitor
        lock["password"]=it.password
        lock["nfc"]=it.nfc
        lock["alart"]=it.alart
        lock["user_logic"]=it.logic
        lock_list.append(lock)
    return lock_list

def auto_login():
    return_info={"state":"0","username":"","phonenum":"","lock_list":{}}
    userid = request.values.get('userID')

    if userid is None:
        return json.dumps(return_info)
    userid = json.loads(userid)

    user = User.query.filter(User.uuid == userid).first()
    if user is None:
        return json.dumps(return_info)
    
    return_info["username"]=user.username
    return_info["phonenum"]=user.phonenum
    

    lock_list=Lock.query.filter(Lock.lockmasteruuid==user.uuid).all()
    return_info["lock_list"]=get_lock_dict(lock_list)
    return_info["state"]="1"
    return json.dumps(return_info)

def change_phonenum():
    return_info={"state":"0"}
    userid = request.values.get('userID')
    if userid is None:
        return json.dumps(return_info)
    userid = json.loads(userid)

    user = User.query.filter(User.uuid == userid).first()
    if user is None:
        return json.dumps(return_info)
    phonenum = request.values.get('phonenum')
    if phonenum is None:
        return json.dumps(return_info)
    phonenum = json.loads(phonenum)
    if phonenum is None:
        return json.dumps(return_info)
    user.phonenum=phonenum
    
    db.session.commit()
    return_info["state"]="1"
    return json.dumps(return_info)

def add_lock():
    return_info={"state":"0"}

    userid = request.values.get('userID')
    if userid is None:
        return json.dumps(return_info)
    userid = json.loads(userid)

    user = User.query.filter(User.uuid == userid).first()
    if user is None:
        return json.dumps(return_info)

    lockname = request.values.get('lockName')
    if lockname is None:
        return json.dumps(return_info)
    lockname = json.loads(lockname)
    
    lock_info=Lock(
        lockname=lockname,
        lockmasteruuid=user.uuid,
        lockid=str(uuid.uuid1()),
        qrcode="0",
        monitor="0",
        password="0",
        nfc="0",
        alart="0",
        logic="none"
    )
    db.session.add(lock_info)
    db.session.commit()
    return_info["state"]="1"
    return json.dumps(return_info)

def delete_lock():
    return_info={"state":"0"}

    lockid = request.values.get('lockID')
    if lockid is None:
        return json.dumps(return_info)
    lockid = json.loads(lockid)
   
    db.session.delete(Lock.query.filter(Lock.lockid == lockid).first())
    db.session.commit()
    return_info["state"]="1"
    return json.dumps(return_info)

def module():
    return_info={"state":"0"}
    #根据锁的id获取锁
    lockid = request.values.get('lockID')
    if lockid is None:
        return json.dumps(return_info)
    lockid = json.loads(lockid)

    lock=Lock.query.filter(Lock.lockid == lockid).first()
    #获得锁的各数据
    qrcode = request.values.get('QRcode')
    if qrcode is None:
        return json.dumps(return_info)
    qrcode = json.loads(qrcode)

    monitor = request.values.get('monitor')
    if monitor is None:
        return json.dumps(return_info)
    monitor = json.loads(monitor)

    password = request.values.get('password')
    if password is None:
        return json.dumps(return_info)
    password = json.loads(password)

    nfc = request.values.get('nfc')
    if nfc is None:
        return json.dumps(return_info)
    nfc = json.loads(nfc)

    alart = request.values.get('alart')
    if alart is None:
        return json.dumps(return_info)
    alart = json.loads(alart)
    #修改锁的各数据
    lock.qrcode=qrcode
    lock.monitor=monitor
    lock.password=password
    lock.nfc=nfc
    lock.alart=alart
    #
    db.session.commit()
    return_info["state"]="1"
    return json.dumps(return_info)

@account_app.route('/', methods=['POST'])
def deal():
    port=request.values.get('port')
    port=json.loads(port)
    if port=="login":
        return login()
    elif port=="register":
        return register()
    elif port=="auto_login":
        return auto_login()
    elif port=="change_phonenum":
        return change_phonenum()
    elif port=="add_lock":
        return add_lock()
    elif port=="delete_lock":
        return delete_lock()
    elif port=="module":
        return module()
    
    return json.dumps("deal error")
