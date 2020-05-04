# app.py

#####系统模块
from functools import wraps
from flask import Flask, request, render_template, redirect, url_for, flash, session
import os

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_, or_
from flask import Flask
#####

#####自定义模块
import config.config as config
from db_manage.sql import db
#from account_manage.account_models import User
from account_manage.account_views import account_app
#####

app = Flask(__name__)

#从config文件中读取配置
app.config.from_object(config.Config)

#初始化数据库对象
db.init_app(app)


@app.before_first_request
def create_db():
    #每次启动更新一下，创建未创建过的表
    #db.drop_all()
    db.create_all()


app.register_blueprint(account_app)

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5050,debug=True)
