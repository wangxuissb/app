# -*- coding: utf-8 -*-
from flask import Flask, jsonify, request, abort, make_response
from sqlalchemy import create_engine, MetaData, and_, desc, asc
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from flask.ext.sqlalchemy import SQLAlchemy
from .. import db,db_session,session
from . import main


UserIdNum = [0]



# *****************************用户相关*****************************
class User(db.Model):
    __tablename__ = 'user'
    # -----------------------------必要信息-------------------------
    # ID
    UserId = db.Column(db.Integer, primary_key=True)
    # 电话号
    TelPhone = db.Column(db.String)
    # 密码
    PassWord = db.Column(db.String)

    # -----------------------------扩展信息-------------------------
    # 昵称
    NickName = db.Column(db.String)
    # 学校
    SchoolName = db.Column(db.String)
    # 专业
    Major = db.Column(db.String)
    # 学历
    Education = db.Column(db.String)
    # 个性签名
    Sign = db.Column(db.String)
    # 头像url
    Avatar = db.Column(db.String)

    # -----------------------------权限信息-------------------------
    # 是否封号
    IsBan = db.Column(db.Boolean)
    # 是否可以发布
    IsPublish = db.Column(db.Boolean)
    # 是否有开发权限
    IsDevelop = db.Column(db.Boolean)

    # -----------------------------关联信息-------------------------
    # 出售的帖子
    SaleBooks = db.Column(db.String)
    # 求购的帖子
    BuyBooks = db.Column(db.String)
    # 关注的人
    StarPeoples = db.Column(db.String)
    # 关注我的人
    StaredPeoples = db.Column(db.String)
    # 收藏的帖子
    StarBooks = db.Column(db.String)
    # 购物车
    Shopping = db.Column(db.String)
    # 我的订单
    OrderList = db.Column(db.String)
    # 此人的评论
    Comment = db.Column(db.String)

    # -----------------------------其他信息-------------------------
    # 用户类型（个人，书店）
    Type = db.Column(db.String)
    # 经验
    Ex = db.Column(db.INTEGER)
    # 积分
    Gold = db.Column(db.INTEGER)
    # 收货地址
    Location = db.Column(db.String)
    # 用户注册时间
    CreatedAt = db.Column(db.INTEGER)
    # 上次登录时间
    LastLoginTime = db.Column(db.INTEGER)

    def __int__(self, UserId, TelPhone, PassWord, NickName, SchoolName, Major, Education,
                Sign, Avatar, IsBan, IsPublish, IsDevelop, SaleBooks, BuyBooks, StarBooks, StaredPeoples,
                StarPeoples, Shopping, OrderList, Location, Ex, Gold, CreatedAt, LastLoginTime, Comment):
        self.UserId = UserId
        self.TelPhone = TelPhone
        self.PassWord = PassWord
        self.NickName = NickName
        self.SchoolName = SchoolName
        self.Major = Major
        self.Education = Education
        self.Sign = Sign
        self.Avatar = Avatar
        self.IsBan = IsBan
        self.IsPublish = IsPublish
        self.IsDevelop = IsDevelop
        self.SaleBooks = SaleBooks
        self.BuyBooks = BuyBooks
        self.StarBooks = StarBooks
        self.StaredPeoples = StaredPeoples
        self.StarPeoples = StarPeoples
        self.Ex = Ex
        self.Gold = Gold
        self.Shopping = Shopping
        self.Location = Location
        self.OrderList = OrderList
        self.CreatedAt = CreatedAt
        self.LastLoginTime = LastLoginTime
        self.Comment = Comment

    def __repr__(self):
        return ''

		
@main.teardown_request
def shutdown_session(exception=None):
    db_session.remove()


@main.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not Found'}), 404)


@main.route('/', methods=['GET', 'POST'])
def index():
    return '欢迎来到e书淘'

# 按条件查找用户
@main.route('/api/userinfo/find', methods=['POST'])
def FindAllUser():
    if request.json['Type'] == 'SchoolName':
        skip = request.json['Skip']
        limit = request.json['Limit']
        schoolname = request.json['SchoolName']
        userList = User.query.filter_by(SchoolName=schoolname).limit(limit).offset(skip).all()
        for user in userList:
            return jsonify({'UserId': user.UserId})


# 查找单个用户
@main.route('/api/userinfo/find/<int:Uid>', methods=['GET'])
def FindUserById(Uid):
    get = User.query.filter_by(UserId=Uid).first()
    return jsonify({'UserId': get.UserId, 'TelPhone': get.TelPhone, 'NickName': get.NickName,
                    'SchoolName': get.SchoolName, 'Major': get.Major, 'Education': get.Education,
                    'Sign': get.Sign, 'Avatar': get.Avatar, 'IsBan': get.IsBan,
                    'IsPublish': get.IsPublish, 'IsDevelop': get.IsDevelop, 'Ex': get.Ex, 'Gold': get.Gold,
                    'LastLoginTime': get.LastLoginTime, 'SaleBooks': get.SaleBooks, 'BuyBooks': get.BuyBooks,
                    'Shopping': get.Shopping, 'Location': get.Location, 'OrderList': get.OrderList,
                    'StarPeoples': get.StarPeoples, 'StaredPeoples': get.StaredPeoples,
                    'StarBooks': get.StarBooks, 'CreatedAt': get.CreatedAt, 'Comment': get.Comment})


# 登陆
@main.route('/api/userinfo/login/<Tel>&<Psw>&<Time>', methods=['POST'])
def Login(Tel, Psw, Time):
    get = User.query.filter_by(TelPhone=Tel).first()
    id = get.UserId
    if get.PassWord == Psw:
        get.LastLoginTime = Time
        session.merge(get)
        session.commit()
        session.close()
        return jsonify({'Message': '成功', 'UserId': id})
    else:
        return jsonify({'Message': '密码错误', 'UserId': ''})


# 注册
@main.route('/api/userinfo/signup', methods=['POST'])
def SignUp():
    teluser = User.query.filter_by(TelPhone=request.json['TelPhone']).first()
    nameuser = User.query.filter_by(TelPhone=request.json['NickName']).first()
    if teluser:
        return jsonify({'Message': '手机号码存在'})
    elif nameuser:
        return jsonify({'Message': '昵称存在'})
    else:
        u = User(TelPhone=request.json['TelPhone'])
        u.NickName = request.json['NickName']
        u.PassWord = request.json['PassWord']
        u.SchoolName = request.json['SchoolName']
        u.Major = request.json['Major']
        u.Education = request.json['Education']
        u.Sign = request.json['Sign']
        u.Avatar = request.json['Avatar']
        u.IsBan = False
        u.IsDevelop = False
        u.IsPublish = False
        u.Ex = 0
        u.Gold = 0
        u.CreatedAt = request.json['CreatedAt']
        u.LastLoginTime = request.json['LastLoginTime']
        u.SaleBooks = ''
        u.BuyBooks = ''
        u.StaredPeoples = ''
        u.StarPeoples = ''
        u.StarBooks = ''
        u.Location = ''
        u.Shopping = ''
        u.OrderList = ''
        u.Comment = ''
        session.add(u)
        session.commit()
        session.close()
        return jsonify({'Message': '注册成功'})


# 更新资料
@main.route('/api/userinfo/update', methods=['POST'])
def UpdateUser():
    u = User(UserId=request.json['UserId'])
    u.TelPhone = request.json['TelPhone']
    u.NickName = request.json['NickName']
    u.PassWord = request.json['PassWord']
    u.SchoolName = request.json['SchoolName']
    u.Major = request.json['Major']
    u.Education = request.json['Education']
    u.Sign = request.json['Sign']
    u.Avatar = request.json['Avatar']
    u.IsBan = request.json['IsBan']
    u.IsPublish = request.json['IsPublish']
    u.IsDevelop = request.json['IsDevelop']
    u.Ex = request.json['Ex']
    u.Gold = request.json['Gold']
    u.CreatedAt = request.json['CreatedAt']
    u.LastLoginTime = request.json['LastLoginTime']
    u.SaleBooks = request.json['SaleBooks']
    u.BuyBooks = request.json['BuyBooks']
    u.StarBooks = request.json['StarBooks']
    u.StarPeoples = request.json['StarPeoples']
    u.StaredPeoples = request.json['StaredPeoples']
    u.Shopping = request.json['Shopping']
    u.OrderList = request.json['OrderList']
    u.Location = request.json['Location']
    u.Comment = request.json['Comment']
    session.merge(u)
    session.commit()
    session.close()
    return jsonify({'Message': '更新成功'})


