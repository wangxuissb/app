# -*- coding: utf-8 -*-
from flask import Flask, jsonify, request, abort, make_response
from sqlalchemy import create_engine, MetaData, and_, desc, asc
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from flask.ext.sqlalchemy import SQLAlchemy
from .. import db, db_session, session
from . import main

UserIdNum = [0]


@main.teardown_request
def shutdown_session(exception=None):
    db_session.remove()


@main.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not Found'}), 404)


@main.route('/', methods=['GET', 'POST'])
def index():
    return '欢迎来到e书淘'


# *****************************用户相关*****************************
class User(db.Model):
    # 共计28项
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
    # 0是个人用户 1是书店用户
    Type = db.Column(db.String)
    # 余额
    Money = db.Column(db.DECIMAL)
    # 经验
    Ex = db.Column(db.INTEGER)
    # 积分
    Gold = db.Column(db.INTEGER)
    # 收货地址
    Location = db.Column(db.String)
    # 用户注册时间
    CreatedAt = db.Column(db.BIGINT)
    # 上次登录时间
    LastLoginTime = db.Column(db.BIGINT)
    # 上次签到时间
    LastPastTime = db.Column(db.BIGINT)

    def __int__(self, UserId, TelPhone, PassWord, NickName, SchoolName, Major, Education,
                Sign, Avatar, IsBan, IsPublish, IsDevelop, SaleBooks, BuyBooks, StarBooks, StaredPeoples,
                StarPeoples, Shopping, OrderList, Location, Ex, Gold, CreatedAt, LastLoginTime, Comment, Type,
                LastPastTime, Money):
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
        self.Money = Money
        self.Ex = Ex
        self.Gold = Gold
        self.Shopping = Shopping
        self.Location = Location
        self.OrderList = OrderList
        self.CreatedAt = CreatedAt
        self.LastLoginTime = LastLoginTime
        self.Comment = Comment
        self.Type = Type
        self.LastPastTime = LastPastTime

    def __repr__(self):
        return ''


# 查找单个用户
@main.route('/api/userinfo/find/<int:Uid>', methods=['GET'])
def FindUserById(Uid):
    get = User.query.filter_by(UserId=Uid).first()
    return jsonify({'UserId': get.UserId, 'TelPhone': get.TelPhone, 'NickName': get.NickName,
                    'SchoolName': get.SchoolName, 'Major': get.Major, 'Education': get.Education,
                    'Sign': get.Sign, 'Avatar': get.Avatar, 'IsBan': get.IsBan,
                    'IsPublish': get.IsPublish, 'IsDevelop': get.IsDevelop, 'Money': get.Money, 'Ex': get.Ex,
                    'Gold': get.Gold, 'LastLoginTime': get.LastLoginTime, 'SaleBooks': get.SaleBooks,
                    'BuyBooks': get.BuyBooks, 'PassWord': get.PassWord,
                    'Shopping': get.Shopping, 'Location': get.Location, 'OrderList': get.OrderList,
                    'StarPeoples': get.StarPeoples, 'StaredPeoples': get.StaredPeoples,
                    'StarBooks': get.StarBooks, 'CreatedAt': get.CreatedAt, 'Comment': get.Comment, 'Type': get.Type,
                    'LastPastTime': get.LastPastTime})


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
        u.Money = 0
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
        u.Type = request.json['Type']
        u.LastPastTime = 0
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
    u.Money = request.json['Money']
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
    u.Type = request.json['Type']
    u.LastPastTime = request.json['LastPastTime']
    session.merge(u)
    session.commit()
    session.close()
    return jsonify({'Message': '更新成功'})


# *****************************帖子相关*****************************
# *****************************出   售*****************************
class Sale(db.Model):
    # 共计19项
    __tablename__ = 'sale'
    # ID
    SaleId = db.Column(db.Integer, primary_key=True)
    # 用户ID
    UserId = db.Column(db.Integer)
    # 书名
    BookName = db.Column(db.String)
    # 作者
    Author = db.Column(db.String)
    # 分类
    Classify = db.Column(db.String)
    # 出版社
    Publish = db.Column(db.String)
    # Isbn号
    Isbn = db.Column(db.String)
    # 是否出售
    IsSale = db.Column(db.Boolean)
    # 学校
    SchoolName = db.Column(db.String)
    # 位置
    Location = db.Column(db.String)
    # 价格
    NewPrice = db.Column(db.DECIMAL)
    # 新旧程度
    OldOrNew = db.Column(db.Integer)
    # 原价
    OldPrice = db.Column(db.String)
    # 备注
    Remark = db.Column(db.String)
    # 联系电话
    Tel = db.Column(db.String)
    # 其他
    Other = db.Column(db.String)
    # 发布时间
    CreatedAt = db.Column(db.BIGINT)
    # 图片url
    PicList = db.Column(db.String)
    # 评论
    Comment = db.Column(db.String)


def __int__(self, SaleId, UserId, BookName, Author, Classify, Publish, IsSale, Location
            , NewPrice, OldOrNew, OldPrice, Remark, Tel, Other, CreatedAt, PicList
            , Isbn, Comment, SchoolName):
    self.SaleId = SaleId
    self.UserId = UserId
    self.BookName = BookName
    self.Author = Author
    self.Classify = Classify
    self.Publish = Publish
    self.IsSale = IsSale
    self.Location = Location
    self.NewPrice = NewPrice
    self.OldOrNew = OldOrNew
    self.OldPrice = OldPrice
    self.Remark = Remark
    self.Tel = Tel
    self.SchoolName = SchoolName
    self.Other = Other
    self.CreatedAt = CreatedAt
    self.PicList = PicList
    self.Isbn = Isbn
    self.Comment = Comment


def __repr__(self):
    return ''


# 新建出售订单
@main.route('/api/bookinfo/create/sale', methods=['POST'])
def CreateSale():
    s = Sale(UserId=request.json['UserId'])
    s.BookName = request.json['BookName']
    s.Author = request.json['Author']
    s.Classify = request.json['Classify']
    s.Publish = request.json['Publish']
    s.IsSale = request.json['IsSale']
    s.Location = request.json['Location']
    s.NewPrice = request.json['NewPrice']
    s.OldOrNew = request.json['OldOrNew']
    s.OldPrice = request.json['OldPrice']
    s.Remark = request.json['Remark']
    s.Tel = request.json['Tel']
    s.Other = request.json['Other']
    s.CreatedAt = request.json['CreatedAt']
    s.PicList = request.json['PicList']
    s.Isbn = request.json['Isbn']
    s.SchoolName = request.json['SchoolName']
    s.Comment = ''
    session.add(s)
    session.commit()
    session.close()
    return jsonify({'Message': '成功'})


# 查询出售
# 无序0
# 价钱从低到高10，从高到底11
# 新旧从新到旧20，从旧到新21
# desc降序，asc升序
@main.route('/api/bookinfo/find/sale', methods=['POST'])
def FindAllSale():
    type = request.json['Type']
    skip = request.json['Skip']
    limit = request.json['Limit']
    schoolname = request.json['SchoolName']
    issale = request.json['Sale']
    if type == 0:
        if schoolname == '':
            booklist = Sale.query.filter(Sale.IsSale == issale).order_by(desc(Sale.OldOrNew)).limit(limit).offset(
                skip).all()
        else:
            booklist = Sale.query.filter(and_(Sale.SchoolName.like(schoolname), Sale.IsSale == issale)).limit(
                limit).offset(skip).all()
    elif type == 10:
        if schoolname == '':
            booklist = Sale.query.filter(Sale.IsSale == issale).order_by(
                asc(Sale.NewPrice)).limit(limit).offset(skip).all()
        else:
            booklist = Sale.query.filter(and_(Sale.SchoolName.like(schoolname), Sale.IsSale == issale)).order_by(
                asc(Sale.NewPrice)).limit(limit).offset(skip).all()
    elif type == 11:
        if schoolname == '':
            booklist = Sale.query.filter(Sale.IsSale == issale).order_by(
                desc(Sale.NewPrice)).limit(limit).offset(skip).all()
        else:
            booklist = Sale.query.filter(and_(Sale.SchoolName.like(schoolname), Sale.IsSale == issale)).order_by(
                desc(Sale.NewPrice)).limit(limit).offset(skip).all()
    elif type == 20:
        if schoolname == '':
            booklist = Sale.query.filter(Sale.IsSale == issale).order_by(
                asc(Sale.OldOrNew)).limit(limit).offset(skip).all()
        else:
            booklist = Sale.query.filter(and_(Sale.SchoolName.like(schoolname), Sale.IsSale == issale)).order_by(
                asc(Sale.OldOrNew)).limit(limit).offset(skip).all()
    elif type == 21:
        if schoolname == '':
            booklist = Sale.query.filter(Sale.IsSale == issale).order_by(Sale.OldOrNew.desc()).limit(
                limit).offset(skip).all()
        else:
            booklist = Sale.query.filter(and_(Sale.SchoolName.like(schoolname), Sale.IsSale == issale)).order_by(
                desc(Sale.OldOrNew)).limit(limit).offset(skip).all()
    elif type == 1020:
        if schoolname == '':
            booklist = Sale.query.filter(Sale.IsSale == issale).order_by(
                asc(Sale.NewPrice)).order_by(
                asc(Sale.OldOrNew)).limit(limit).offset(skip).all()
        else:
            booklist = Sale.query.filter(and_(Sale.SchoolName.like(schoolname), Sale.IsSale == issale)).order_by(
                asc(Sale.NewPrice)).order_by(asc(Sale.OldOrNew)).limit(limit).offset(skip).all()
    elif type == 1021:
        if schoolname == '':
            booklist = Sale.query.filter(Sale.IsSale == issale).order_by(asc(Sale.NewPrice)).order_by(
                desc(Sale.OldOrNew)).limit(limit).offset(skip).all()
        else:
            booklist = Sale.query.filter(and_(Sale.SchoolName.like(schoolname), Sale.IsSale == issale)).order_by(
                asc(Sale.NewPrice)).order_by(desc(Sale.OldOrNew)).limit(limit).offset(skip).all()
    elif type == 1120:
        if schoolname == '':
            booklist = Sale.query.filter(Sale.IsSale == issale).order_by(desc(Sale.NewPrice)).order_by(
                asc(Sale.OldOrNew)).limit(limit).offset(skip).all()
        else:
            booklist = Sale.query.filter(and_(Sale.SchoolName.like(schoolname), Sale.IsSale == issale)).order_by(
                desc(Sale.NewPrice)).order_by(asc(Sale.OldOrNew)).limit(limit).offset(skip).all()
    elif type == 1121:
        if schoolname == '':
            booklist = Sale.query.filter(Sale.IsSale == issale).order_by(
                desc(Sale.NewPrice)).order_by(
                desc(Sale.OldOrNew)).limit(limit).offset(skip).all()
        else:
            booklist = Sale.query.filter(and_(Sale.SchoolName.like(schoolname), Sale.IsSale == issale)).order_by(
                desc(Sale.NewPrice)).order_by(desc(Sale.OldOrNew)).limit(limit).offset(skip).all()
    elif type == 2010:
        if schoolname == '':
            booklist = Sale.query.filter(Sale.IsSale == issale).order_by(
                asc(Sale.OldOrNew)).order_by(
                asc(Sale.NewPrice)).limit(limit).offset(skip).all()
        else:
            booklist = Sale.query.filter(and_(Sale.SchoolName.like(schoolname), Sale.IsSale == issale)).order_by(
                asc(Sale.OldOrNew)).order_by(asc(Sale.NewPrice)).limit(limit).offset(skip).all()
    elif type == 2011:
        if schoolname == '':
            booklist = Sale.query.filter(Sale.IsSale == issale).order_by(
                asc(Sale.OldOrNew)).order_by(
                desc(Sale.NewPrice)).limit(limit).offset(skip).all()
        else:
            booklist = Sale.query.filter(and_(Sale.SchoolName.like(schoolname), Sale.IsSale == issale)).order_by(
                asc(Sale.OldOrNew)).order_by(desc(Sale.NewPrice)).limit(limit).offset(skip).all()
    elif type == 2110:
        if schoolname == '':
            booklist = Sale.query.filter(Sale.IsSale == issale).order_by(
                desc(Sale.OldOrNew)).order_by(
                asc(Sale.NewPrice)).limit(limit).offset(skip).all()
        else:
            booklist = Sale.query.filter(and_(Sale.SchoolName.like(schoolname), Sale.IsSale == issale)).order_by(
                desc(Sale.OldOrNew)).order_by(asc(Sale.NewPrice)).limit(limit).offset(skip).all()
    elif type == 2111:
        if schoolname == '':
            booklist = Sale.query.filter(Sale.IsSale == issale).order_by(
                desc(Sale.OldOrNew)).order_by(
                desc(Sale.NewPrice)).limit(limit).offset(skip).all()
        else:
            booklist = Sale.query.filter(and_(Sale.SchoolName.like(schoolname), Sale.IsSale == issale)).order_by(
                desc(Sale.OldOrNew)).order_by(desc(Sale.NewPrice)).limit(limit).offset(skip).all()
    if booklist:
        newlist = list()
        for book in booklist:
            newlist.append(book.SaleId)
        return jsonify({'SaleId': newlist})
    else:
        return jsonify({'Message': '无结果'})


# 根据id查询
@main.route('/api/bookinfo/find/sale/<int:id>', methods=['GET'])
def FindSaleById(id):
    get = Sale.query.filter_by(SaleId=id).first()
    return jsonify({'SaleId': get.SaleId, 'UserId': get.UserId, 'BookName': get.BookName,
                    'Author': get.Author, 'Classify': get.Classify, 'Publish': get.Publish,
                    'IsSale': get.IsSale, 'Location': get.Location, 'NewPrice': get.NewPrice,
                    'OldOrNew': get.OldOrNew, 'OldPrice': get.OldPrice, 'Remark': get.Remark, 'Tel': get.Tel,
                    'Other': get.Other, 'CreatedAt': get.CreatedAt, 'PicList': get.PicList,
                    'Isbn': get.Isbn, 'Comment': get.Comment, 'SchoolName': get.SchoolName})


# 更新出售
@main.route('/api/bookinfo/update/sale', methods=['POST'])
def UpdateSale():
    s = Sale(SaleId=request.json['SaleId'])
    s.IsSale = request.json['IsSale']
    s.Comment = request.json['Comment']
    session.merge(s)
    session.commit()
    session.close()
    return jsonify({'Message': '成功'})


# 按书名搜索
@main.route('/api/bookinfo/find/sale/bookname', methods=['POST'])
def FindSaleBookName():
    bookname = request.json['BookName']
    skip = request.json['Skip']
    limit = request.json['Limit']
    booklist = Sale.query.filter(Sale.BookName.like("%" + bookname + "%")).limit(
        limit).offset(skip).all()
    if booklist:
        newlist = list()
        for book in booklist:
            newlist.append(book.SaleId)
        return jsonify({'SaleId': newlist})
    else:
        return jsonify({'Message': '无结果'})
