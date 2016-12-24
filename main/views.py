# -*- coding: utf-8 -*-
import hashlib
import random
import requests
from flask import Flask, jsonify, request, abort, make_response
from sqlalchemy import create_engine, MetaData, and_, or_, desc, asc
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from flask.ext.sqlalchemy import SQLAlchemy
from .. import db, db_session, session
from . import main
import json, time, urllib2

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


# *****************************主页相关内容*****************************
class App(db.Model):
    __tablename__ = 'app'
    AppId = db.Column(db.Integer, primary_key=True)
    Type = db.Column(db.String)
    State = db.Column(db.INTEGER)
    Content = db.Column(db.String)

    def __int__(self, AppId, State, Content, Type):
        self.AppId = AppId
        self.State = State
        self.Content = Content
        self.Type = Type

    def __repr__(self):
        return ''


# app状态
@main.route('/api/appinfo/state', methods=['GET'])
def getAppState():
    app = App.query.filter(App.Type.like('状态')).first()
    return jsonify({'Message': '成功', 'Data': app.State})


# 获取主页推荐
@main.route('/api/appinfo/foryou', methods=['POST'])
def getForYou():
    schoolname = request.json['School']
    major = request.json['Major']
    issale = False
    foryoulist = list()
    booklist2 = App.query.filter(App.Type.like('推荐')).all()
    if booklist2:
        for app in booklist2:
            book2 = Sale.query.filter_by(SaleId=app.Content).first()
            NewPrice2 = str(book2.NewPrice)
            getuser2 = User.query.filter_by(UserId=book2.UserId).first()
            money2 = str(getuser2.Money)
            userdata2 = {'UserId': getuser2.UserId, 'TelPhone': getuser2.TelPhone, 'NickName': getuser2.NickName,
                         'SchoolName': getuser2.SchoolName, 'Major': getuser2.Major, 'Education': getuser2.Education,
                         'Sign': getuser2.Sign, 'Avatar': getuser2.Avatar, 'IsBan': getuser2.IsBan,
                         'IsPublish': getuser2.IsPublish, 'IsDevelop': getuser2.IsDevelop, 'Money': money2,
                         'Ex': getuser2.Ex, 'Gold': getuser2.Gold, 'LastLoginTime': getuser2.LastLoginTime,
                         'PassWord': getuser2.PassWord, 'Location': getuser2.Location,
                         'CreatedAt': getuser2.CreatedAt, 'Type': getuser2.Type,
                         'LastPastTime': getuser2.LastPastTime, 'QQ': getuser2.QQ, 'WeChat': getuser2.WeChat,
                         'IMToken': getuser2.IMToken}
            data2 = {'SaleId': book2.SaleId, 'UserId': book2.UserId, 'BookName': book2.BookName,
                     'Author': book2.Author, 'Classify': book2.Classify, 'Publish': book2.Publish,
                     'IsSale': book2.IsSale, 'Location': book2.Location, 'NewPrice': NewPrice2,
                     'OldOrNew': book2.OldOrNew, 'OldPrice': book2.OldPrice, 'Remark': book2.Remark,
                     'Tel': book2.Tel, 'Count': book2.Count, 'isOffLine': book2.isOffLine,
                     'Label': book2.Label, 'CreatedAt': book2.CreatedAt, 'PicList': book2.PicList,
                     'Isbn': book2.Isbn, 'SchoolName': book2.SchoolName, 'ShopId': book2.ShopId,
                     'Belong': book2.Belong, 'User': userdata2}
            foryoulist.append(data2)
    booklist = Sale.query.filter(and_(Sale.SchoolName.like(schoolname), Sale.IsSale == issale)).order_by(
        desc(Sale.SaleId)).limit(10).all()
    if booklist:
        for book in booklist:
            NewPrice = str(book.NewPrice)
            getuser = User.query.filter_by(UserId=book.UserId).first()
            money = str(getuser.Money)
            userdata = {'UserId': getuser.UserId, 'TelPhone': getuser.TelPhone, 'NickName': getuser.NickName,
                        'SchoolName': getuser.SchoolName, 'Major': getuser.Major, 'Education': getuser.Education,
                        'Sign': getuser.Sign, 'Avatar': getuser.Avatar, 'IsBan': getuser.IsBan,
                        'IsPublish': getuser.IsPublish, 'IsDevelop': getuser.IsDevelop, 'Money': money,
                        'Ex': getuser.Ex, 'Gold': getuser.Gold, 'LastLoginTime': getuser.LastLoginTime,
                        'PassWord': getuser.PassWord, 'Location': getuser.Location,
                        'CreatedAt': getuser.CreatedAt, 'Type': getuser.Type,
                        'LastPastTime': getuser.LastPastTime, 'QQ': getuser.QQ, 'WeChat': getuser.WeChat,
                        'IMToken': getuser.IMToken}
            data = {'SaleId': book.SaleId, 'UserId': book.UserId, 'BookName': book.BookName,
                    'Author': book.Author, 'Classify': book.Classify, 'Publish': book.Publish,
                    'IsSale': book.IsSale, 'Location': book.Location, 'NewPrice': NewPrice,
                    'OldOrNew': book.OldOrNew, 'OldPrice': book.OldPrice, 'Remark': book.Remark,
                    'Tel': book.Tel, 'Count': book.Count, 'isOffLine': book.isOffLine,
                    'Label': book.Label, 'CreatedAt': book.CreatedAt, 'PicList': book.PicList,
                    'Isbn': book.Isbn, 'SchoolName': book.SchoolName, 'ShopId': book.ShopId,
                    'Belong': book.Belong, 'User': userdata}
            foryoulist.append(data)
    booklist1 = Sale.query.filter(and_(Sale.BookName.like("%" + major + "%"), Sale.IsSale == issale)).order_by(
        desc(Sale.SaleId)).limit(10).all()
    if booklist1:
        for book1 in booklist1:
            NewPrice1 = str(book1.NewPrice)
            getuser1 = User.query.filter_by(UserId=book1.UserId).first()
            money1 = str(getuser1.Money)
            userdata1 = {'UserId': getuser1.UserId, 'TelPhone': getuser1.TelPhone, 'NickName': getuser1.NickName,
                         'SchoolName': getuser1.SchoolName, 'Major': getuser1.Major, 'Education': getuser1.Education,
                         'Sign': getuser1.Sign, 'Avatar': getuser1.Avatar, 'IsBan': getuser1.IsBan,
                         'IsPublish': getuser1.IsPublish, 'IsDevelop': getuser1.IsDevelop, 'Money': money1,
                         'Ex': getuser1.Ex, 'Gold': getuser1.Gold, 'LastLoginTime': getuser1.LastLoginTime,
                         'PassWord': getuser1.PassWord, 'Location': getuser1.Location,
                         'CreatedAt': getuser1.CreatedAt, 'Type': getuser1.Type,
                         'LastPastTime': getuser1.LastPastTime, 'QQ': getuser1.QQ, 'WeChat': getuser1.WeChat,
                         'IMToken': getuser1.IMToken}
            data1 = {'SaleId': book1.SaleId, 'UserId': book1.UserId, 'BookName': book1.BookName,
                     'Author': book1.Author, 'Classify': book1.Classify, 'Publish': book1.Publish,
                     'IsSale': book1.IsSale, 'Location': book1.Location, 'NewPrice': NewPrice1,
                     'OldOrNew': book1.OldOrNew, 'OldPrice': book1.OldPrice, 'Remark': book1.Remark,
                     'Tel': book1.Tel, 'Count': book1.Count, 'isOffLine': book1.isOffLine,
                     'Label': book1.Label, 'CreatedAt': book1.CreatedAt, 'PicList': book1.PicList,
                     'Isbn': book1.Isbn, 'SchoolName': book1.SchoolName, 'ShopId': book1.ShopId,
                     'Belong': book1.Belong, 'User': userdata1}
            foryoulist.append(data1)
    booklist0 = Sale.query.filter(Sale.IsSale == issale).order_by(
        desc(Sale.SaleId)).limit(5).all()
    if booklist0:
        for book0 in booklist0:
            NewPrice0 = str(book0.NewPrice)
            getuser0 = User.query.filter_by(UserId=book0.UserId).first()
            money0 = str(getuser0.Money)
            userdata0 = {'UserId': getuser0.UserId, 'TelPhone': getuser0.TelPhone, 'NickName': getuser0.NickName,
                         'SchoolName': getuser0.SchoolName, 'Major': getuser0.Major, 'Education': getuser0.Education,
                         'Sign': getuser0.Sign, 'Avatar': getuser0.Avatar, 'IsBan': getuser0.IsBan,
                         'IsPublish': getuser0.IsPublish, 'IsDevelop': getuser0.IsDevelop, 'Money': money0,
                         'Ex': getuser0.Ex, 'Gold': getuser0.Gold, 'LastLoginTime': getuser0.LastLoginTime,
                         'PassWord': getuser0.PassWord, 'Location': getuser0.Location,
                         'CreatedAt': getuser0.CreatedAt, 'Type': getuser0.Type,
                         'LastPastTime': getuser0.LastPastTime, 'QQ': getuser0.QQ, 'WeChat': getuser0.WeChat,
                         'IMToken': getuser0.IMToken}
            data0 = {'SaleId': book0.SaleId, 'UserId': book0.UserId, 'BookName': book0.BookName,
                     'Author': book0.Author, 'Classify': book0.Classify, 'Publish': book0.Publish,
                     'IsSale': book0.IsSale, 'Location': book0.Location, 'NewPrice': NewPrice0,
                     'OldOrNew': book0.OldOrNew, 'OldPrice': book0.OldPrice, 'Remark': book0.Remark,
                     'Tel': book0.Tel, 'Count': book0.Count, 'isOffLine': book0.isOffLine,
                     'Label': book0.Label, 'CreatedAt': book0.CreatedAt, 'PicList': book0.PicList,
                     'Isbn': book0.Isbn, 'SchoolName': book0.SchoolName, 'ShopId': book0.ShopId,
                     'Belong': book0.Belong, 'User': userdata0}
            foryoulist.append(data0)
    return jsonify({'Message': '成功', 'Data': foryoulist})


# *****************************用户相关*****************************
class User(db.Model):
    # 共计22项
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
    # -----------------------------其他信息-------------------------
    # qq
    QQ = db.Column(db.String)
    # 微信
    WeChat = db.Column(db.String)
    # 用户类型（个人）
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

    # IM token
    IMToken = db.Column(db.String)

    def __int__(self, UserId, TelPhone, PassWord, NickName, SchoolName, Major, Education,
                Sign, Avatar, IsBan, IsPublish, IsDevelop, Location, Ex, Gold, CreatedAt, LastLoginTime, Type,
                LastPastTime, Money, QQ, WeChat, IMToken):
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
        self.Money = Money
        self.Ex = Ex
        self.Gold = Gold
        self.Location = Location
        self.CreatedAt = CreatedAt
        self.LastLoginTime = LastLoginTime
        self.Type = Type
        self.LastPastTime = LastPastTime
        self.WeChat = WeChat
        self.QQ = QQ
        self.IMToken = IMToken

    def __repr__(self):
        return ''


# 登陆
@main.route('/api/userinfo/login/<Tel>&<Psw>&<Time>', methods=['POST'])
def Login(Tel, Psw, Time):
    get = User.query.filter_by(TelPhone=Tel).first()
    if get is None:
        return jsonify({'Message': '失败', 'Data': '用户不存在'})
    else:
        if get.PassWord == Psw:
            u = User(UserId=get.UserId)
            u.LastLoginTime = Time
            nonce = str(random.random())
            timestamp = str(int(time.time()) * 1000)
            signature = hashlib.sha1(('hWepl3U2IAw' + nonce + timestamp).encode('utf-8')).hexdigest()
            datainfo = {'userId': 123, 'name': 234, 'portraitUri': '1'}
            headers = {'RC-App-Key': 'ik1qhw09ikf3p', 'RC-Nonce': nonce, 'RC-Timestamp': timestamp,
                       'RC-Signature': signature,
                       'Content-Type': 'application/x-www-form-urlencoded'}
            r = requests.post("http://api.cn.ronghub.com/user/getToken.json", data=datainfo, headers=headers)
            u.IMToken = r.json().get('token')
            money = str(get.Money)
            data = {'UserId': get.UserId, 'TelPhone': get.TelPhone, 'NickName': get.NickName,
                    'SchoolName': get.SchoolName, 'Major': get.Major, 'Education': get.Education,
                    'Sign': get.Sign, 'Avatar': get.Avatar, 'IsBan': get.IsBan,
                    'IsPublish': get.IsPublish, 'IsDevelop': get.IsDevelop, 'Money': money,
                    'Ex': get.Ex, 'Gold': get.Gold, 'LastLoginTime': get.LastLoginTime,
                    'PassWord': get.PassWord, 'Location': get.Location,
                    'CreatedAt': get.CreatedAt, 'Type': get.Type,
                    'LastPastTime': get.LastPastTime, 'QQ': get.QQ, 'WeChat': get.WeChat, 'IMToken': get.IMToken}
            session.merge(u)
            session.commit()
            session.close()
            return jsonify(
                {'Message': '成功', 'Data': data})
        else:
            return jsonify({'Message': '失败', 'Data': '密码错误'})


# 注册
@main.route('/api/userinfo/signup', methods=['POST'])
def SignUp():
    teluser = User.query.filter_by(TelPhone=request.json['TelPhone']).first()
    if teluser:
        return jsonify({'Message': '失败', 'Data': '手机号码已存在'})
    else:
        u = User(TelPhone=request.json['TelPhone'])
        u.NickName = request.json['NickName']
        u.PassWord = request.json['PassWord']
        u.SchoolName = request.json['SchoolName']
        u.Major = request.json['Major']
        u.Education = request.json['Education']
        u.Sign = request.json['Sign']
        u.Avatar = request.json['Avatar']
        u.Type = '个人'
        u.CreatedAt = request.json['CreatedAt']
        u.LastLoginTime = request.json['LastLoginTime']
        u.IsBan = False
        u.IsDevelop = False
        u.IsPublish = False
        u.Ex = 0
        u.Gold = 0
        u.Money = 0
        u.Location = ''
        u.Shopping = ''
        u.QQ = ''
        u.WeChat = ''
        u.LastPastTime = 0
        u.IMToken = ''
        session.add(u)
        session.commit()
        session.close()
        return jsonify({'Message': '成功', 'Data': '注册成功'})


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
    u.Location = request.json['Location']
    u.Type = request.json['Type']
    u.LastPastTime = request.json['LastPastTime']
    u.QQ = request.json['QQ']
    u.WeChat = request.json['WeChat']
    u.IMToken = request.json['IMToken']
    session.merge(u)
    session.commit()
    session.close()
    money = str(u.Money)
    get = User.query.filter_by(UserId=request.json['UserId']).first()
    data = {'UserId': get.UserId, 'TelPhone': get.TelPhone, 'NickName': get.NickName,
            'SchoolName': get.SchoolName, 'Major': get.Major, 'Education': get.Education,
            'Sign': get.Sign, 'Avatar': get.Avatar, 'IsBan': get.IsBan,
            'IsPublish': get.IsPublish, 'IsDevelop': get.IsDevelop, 'Money': money,
            'Ex': get.Ex, 'Gold': get.Gold, 'LastLoginTime': get.LastLoginTime,
            'PassWord': get.PassWord, 'Location': get.Location,
            'CreatedAt': get.CreatedAt, 'Type': get.Type,
            'LastPastTime': get.LastPastTime, 'QQ': get.QQ, 'WeChat': get.WeChat, 'IMToken': get.IMToken}
    return jsonify({'Message': '成功', 'Data': data})


# 查找单个用户
@main.route('/api/userinfo/find/<int:Uid>', methods=['GET'])
def FindUserById(Uid):
    get = User.query.filter_by(UserId=Uid).first()
    money = str(get.Money)
    return jsonify({'UserId': get.UserId, 'TelPhone': get.TelPhone, 'NickName': get.NickName,
                    'SchoolName': get.SchoolName, 'Major': get.Major, 'Education': get.Education,
                    'Sign': get.Sign, 'Avatar': get.Avatar, 'IsBan': get.IsBan,
                    'IsPublish': get.IsPublish, 'IsDevelop': get.IsDevelop, 'Money': money,
                    'Ex': get.Ex, 'Gold': get.Gold, 'LastLoginTime': get.LastLoginTime,
                    'PassWord': get.PassWord, 'Location': get.Location,
                    'CreatedAt': get.CreatedAt, 'Type': get.Type,
                    'LastPastTime': get.LastPastTime, 'QQ': get.QQ, 'WeChat': get.WeChat, 'IMToken': get.IMToken})


# 手机号查找单个用户
@main.route('/api/userinfo/findbytel/<int:Tel>', methods=['GET'])
def FindUserByTel(Tel):
    get = User.query.filter_by(TelPhone=Tel).first()
    if get:
        money = str(get.Money)
        return jsonify({'Message': '成功', 'Data': {'UserId': get.UserId, 'TelPhone': get.TelPhone,
                                                  'NickName': get.NickName,
                                                  'SchoolName': get.SchoolName, 'Major': get.Major,
                                                  'Education': get.Education,
                                                  'Sign': get.Sign, 'Avatar': get.Avatar, 'IsBan': get.IsBan,
                                                  'IsPublish': get.IsPublish, 'IsDevelop': get.IsDevelop,
                                                  'Money': money,
                                                  'Ex': get.Ex, 'Gold': get.Gold, 'LastLoginTime': get.LastLoginTime,
                                                  'PassWord': get.PassWord, 'Location': get.Location,
                                                  'CreatedAt': get.CreatedAt, 'Type': get.Type,
                                                  'LastPastTime': get.LastPastTime, 'QQ': get.QQ,
                                                  'WeChat': get.WeChat, 'IMToken': get.IMToken}})
    else:
        return jsonify({'Message': '成功', 'Data': '该用户不存在'})


# QQ登陆
@main.route('/api/userinfo/loginbyqq/<string:QQ>', methods=['GET'])
def LoginByQQ(QQ):
    get = User.query.filter_by(QQ=QQ).first()
    if get:
        money = str(get.Money)
        return jsonify({'Message': '成功', 'Data': {'UserId': get.UserId, 'TelPhone': get.TelPhone,
                                                  'NickName': get.NickName,
                                                  'SchoolName': get.SchoolName, 'Major': get.Major,
                                                  'Education': get.Education,
                                                  'Sign': get.Sign, 'Avatar': get.Avatar, 'IsBan': get.IsBan,
                                                  'IsPublish': get.IsPublish, 'IsDevelop': get.IsDevelop,
                                                  'Money': money,
                                                  'Ex': get.Ex, 'Gold': get.Gold, 'LastLoginTime': get.LastLoginTime,
                                                  'PassWord': get.PassWord, 'Location': get.Location,
                                                  'CreatedAt': get.CreatedAt, 'Type': get.Type,
                                                  'LastPastTime': get.LastPastTime, 'QQ': get.QQ,
                                                  'WeChat': get.WeChat, 'IMToken': get.IMToken}})
    else:
        return jsonify({'Message': '失败', 'Data': '该用户不存在'})


# *****************************帖子相关*****************************
# *****************************出   售*****************************
class Sale(db.Model):
    # 共计22项
    __tablename__ = 'sale'
    # ID
    SaleId = db.Column(db.Integer, primary_key=True)
    # 书名
    BookName = db.Column(db.String)
    # 作者
    Author = db.Column(db.String)
    # 分类
    Classify = db.Column(db.String)
    # 标签
    Label = db.Column(db.String)
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
    # 发布时间
    CreatedAt = db.Column(db.BIGINT)
    # 图片url
    PicList = db.Column(db.String)
    # 数量
    Count = db.Column(db.INTEGER)
    # 书可以面交
    isOffLine = db.Column(db.Boolean)
    # 来源
    Belong = db.Column(db.String)
    # 用户ID
    UserId = db.Column(db.Integer)
    # 书商ID
    ShopId = db.Column(db.Integer)

    def __int__(self, SaleId, UserId, BookName, Author, Classify, Publish, IsSale, Location
                , NewPrice, OldOrNew, OldPrice, Remark, Tel, CreatedAt, PicList
                , Isbn, SchoolName, Label, Count, isOffLine, ShopId, Belong):
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
        self.CreatedAt = CreatedAt
        self.PicList = PicList
        self.Isbn = Isbn
        self.Label = Label
        self.Count = Count
        self.isOffLine = isOffLine
        self.ShopId = ShopId
        self.Belong = Belong

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
    s.IsSale = False
    s.Location = request.json['Location']
    s.NewPrice = request.json['NewPrice']
    s.OldOrNew = request.json['OldOrNew']
    s.OldPrice = request.json['OldPrice']
    s.Remark = request.json['Remark']
    s.Tel = request.json['Tel']
    s.CreatedAt = request.json['CreatedAt']
    s.PicList = request.json['PicList']
    s.Isbn = request.json['Isbn']
    s.SchoolName = request.json['SchoolName']
    s.Label = request.json['Label']
    s.Count = request.json['Count']
    s.isOffLine = request.json['isOffLine']
    s.Belong = request.json['Belong']
    s.ShopId = request.json['ShopId']
    session.add(s)
    session.commit()
    session.close()
    return jsonify({'Message': '成功', 'Data': '发布成功'})


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
    classify = request.json['Classify']
    issale = False
    if classify == '':
        if type == 0:
            if schoolname == '':
                booklist = Sale.query.filter(Sale.IsSale == issale).order_by(
                    desc(Sale.SaleId)).limit(limit).offset(skip).all()
            else:
                booklist = Sale.query.filter(and_(Sale.SchoolName.like(schoolname), Sale.IsSale == issale)).order_by(
                    desc(Sale.SaleId)).limit(
                    limit).offset(skip).all()
        elif type == 10:
            if schoolname == '':
                booklist = Sale.query.filter(Sale.IsSale == issale).order_by(
                    asc(Sale.NewPrice)).limit(limit).offset(skip).all()
            else:
                booklist = Sale.query.filter(and_(Sale.SchoolName.like(schoolname), Sale.IsSale == issale)).order_by(
                    asc(Sale.NewPrice)).order_by(desc(Sale.SaleId)).limit(limit).offset(skip).all()
        elif type == 11:
            if schoolname == '':
                booklist = Sale.query.filter(Sale.IsSale == issale).order_by(
                    desc(Sale.NewPrice)).order_by(
                    desc(Sale.SaleId)).limit(limit).offset(skip).all()
            else:
                booklist = Sale.query.filter(and_(Sale.SchoolName.like(schoolname), Sale.IsSale == issale)).order_by(
                    desc(Sale.NewPrice)).order_by(
                    desc(Sale.SaleId)).limit(limit).offset(skip).all()
        elif type == 20:
            if schoolname == '':
                booklist = Sale.query.filter(Sale.IsSale == issale).order_by(
                    asc(Sale.OldOrNew)).order_by(
                    desc(Sale.SaleId)).limit(limit).offset(skip).all()
            else:
                booklist = Sale.query.filter(and_(Sale.SchoolName.like(schoolname), Sale.IsSale == issale)).order_by(
                    asc(Sale.OldOrNew)).order_by(
                    desc(Sale.SaleId)).limit(limit).offset(skip).all()
        elif type == 21:
            if schoolname == '':
                booklist = Sale.query.filter(Sale.IsSale == issale).order_by(
                    desc(Sale.OldOrNew)).order_by(
                    desc(Sale.SaleId)).limit(
                    limit).offset(skip).all()
            else:
                booklist = Sale.query.filter(and_(Sale.SchoolName.like(schoolname), Sale.IsSale == issale)).order_by(
                    desc(Sale.OldOrNew)).order_by(
                    desc(Sale.SaleId)).limit(limit).offset(skip).all()
    else:
        if type == 0:
            if schoolname == '':
                booklist = Sale.query.filter(and_(Sale.IsSale == issale, Sale.Classify.like(classify))).order_by(
                    Sale.SaleId.desc()).limit(limit).offset(
                    skip).all()
            else:
                booklist = Sale.query.filter(and_(Sale.SchoolName.like(schoolname), Sale.IsSale == issale,
                                                  Sale.Classify.like(classify))).order_by(
                    desc(Sale.SaleId)).limit(limit).offset(skip).all()
        elif type == 10:
            if schoolname == '':
                booklist = Sale.query.filter(and_(Sale.IsSale == issale, Sale.Classify.like(classify))).order_by(
                    asc(Sale.NewPrice)).order_by(
                    desc(Sale.SaleId)).limit(limit).offset(skip).all()
            else:
                booklist = Sale.query.filter(and_(Sale.SchoolName.like(schoolname), Sale.IsSale == issale,
                                                  Sale.Classify.like(classify))).order_by(
                    asc(Sale.NewPrice)).order_by(desc(Sale.SaleId)).limit(limit).offset(skip).all()
        elif type == 11:
            if schoolname == '':
                booklist = Sale.query.filter(and_(Sale.IsSale == issale, Sale.Classify.like(classify))).order_by(
                    desc(Sale.NewPrice)).order_by(
                    desc(Sale.SaleId)).limit(limit).offset(skip).all()
            else:
                booklist = Sale.query.filter(and_(Sale.SchoolName.like(schoolname), Sale.IsSale == issale,
                                                  Sale.Classify.like(classify))).order_by(
                    desc(Sale.NewPrice)).order_by(
                    desc(Sale.SaleId)).limit(limit).offset(skip).all()
        elif type == 20:
            if schoolname == '':
                booklist = Sale.query.filter(and_(Sale.IsSale == issale, Sale.Classify.like(classify))).order_by(
                    asc(Sale.OldOrNew)).order_by(
                    desc(Sale.SaleId)).limit(limit).offset(skip).all()
            else:
                booklist = Sale.query.filter(and_(Sale.SchoolName.like(schoolname), Sale.IsSale == issale,
                                                  Sale.Classify.like(classify))).order_by(
                    asc(Sale.OldOrNew)).order_by(
                    desc(Sale.SaleId)).limit(limit).offset(skip).all()
        elif type == 21:
            if schoolname == '':
                booklist = Sale.query.filter(and_(Sale.IsSale == issale, Sale.Classify.like(classify))).order_by(
                    desc(Sale.OldOrNew)).order_by(desc(Sale.SaleId)).limit(
                    limit).offset(skip).all()
            else:
                booklist = Sale.query.filter(and_(Sale.SchoolName.like(schoolname), Sale.IsSale == issale,
                                                  Sale.Classify.like(classify))).order_by(
                    desc(Sale.OldOrNew)).order_by(
                    desc(Sale.SaleId)).limit(limit).offset(skip).all()
    if booklist:
        newlist = list()
        for book in booklist:
            NewPrice = str(book.NewPrice)
            getuser = User.query.filter_by(UserId=book.UserId).first()
            money = str(getuser.Money)
            userdata = {'UserId': getuser.UserId, 'TelPhone': getuser.TelPhone, 'NickName': getuser.NickName,
                        'SchoolName': getuser.SchoolName, 'Major': getuser.Major, 'Education': getuser.Education,
                        'Sign': getuser.Sign, 'Avatar': getuser.Avatar, 'IsBan': getuser.IsBan,
                        'IsPublish': getuser.IsPublish, 'IsDevelop': getuser.IsDevelop, 'Money': money,
                        'Ex': getuser.Ex, 'Gold': getuser.Gold, 'LastLoginTime': getuser.LastLoginTime,
                        'PassWord': getuser.PassWord, 'Location': getuser.Location,
                        'CreatedAt': getuser.CreatedAt, 'Type': getuser.Type,
                        'LastPastTime': getuser.LastPastTime, 'QQ': getuser.QQ, 'WeChat': getuser.WeChat,
                        'IMToken': getuser.IMToken}
            data = {'SaleId': book.SaleId, 'UserId': book.UserId, 'BookName': book.BookName,
                    'Author': book.Author, 'Classify': book.Classify, 'Publish': book.Publish,
                    'IsSale': book.IsSale, 'Location': book.Location, 'NewPrice': NewPrice,
                    'OldOrNew': book.OldOrNew, 'OldPrice': book.OldPrice, 'Remark': book.Remark,
                    'Tel': book.Tel, 'Count': book.Count, 'isOffLine': book.isOffLine,
                    'Label': book.Label, 'CreatedAt': book.CreatedAt, 'PicList': book.PicList,
                    'Isbn': book.Isbn, 'SchoolName': book.SchoolName, 'ShopId': book.ShopId,
                    'Belong': book.Belong, 'User': userdata}
            newlist.append(data)
        return jsonify({'Message': '成功', 'Data': newlist})
    else:
        return jsonify({'Message': '失败', 'Data': '没有更多数据了'})


# 更新出售
@main.route('/api/bookinfo/update/sale', methods=['POST'])
def UpdateSale():
    s = Sale(SaleId=request.json['SaleId'])
    s.IsSale = request.json['IsSale']
    s.NewPrice = request.json['NewPrice']
    session.merge(s)
    session.commit()
    session.close()
    return jsonify({'Message': '成功', 'Data': '设置成功'})


# 按书名搜索
@main.route('/api/bookinfo/find/sale/bookname', methods=['POST'])
def FindSaleBookName():
    bookname = request.json['BookName']
    skip = request.json['Skip']
    limit = request.json['Limit']
    booklist = Sale.query.filter(or_(Sale.BookName.like("%" + bookname + "%"), Sale.Author.like("%" + bookname + "%"),
                                     Sale.Publish.like("%" + bookname + "%"),
                                     Sale.Classify.like("%" + bookname + "%"))).order_by(
        desc(Sale.SaleId)).limit(
        limit).offset(skip).all()
    if booklist:
        newlist = list()
        for book in booklist:
            NewPrice = str(book.NewPrice)
            getuser = User.query.filter_by(UserId=book.UserId).first()
            money = str(getuser.Money)
            userdata = {'UserId': getuser.UserId, 'TelPhone': getuser.TelPhone, 'NickName': getuser.NickName,
                        'SchoolName': getuser.SchoolName, 'Major': getuser.Major, 'Education': getuser.Education,
                        'Sign': getuser.Sign, 'Avatar': getuser.Avatar, 'IsBan': getuser.IsBan,
                        'IsPublish': getuser.IsPublish, 'IsDevelop': getuser.IsDevelop, 'Money': money,
                        'Ex': getuser.Ex, 'Gold': getuser.Gold, 'LastLoginTime': getuser.LastLoginTime,
                        'PassWord': getuser.PassWord, 'Location': getuser.Location,
                        'CreatedAt': getuser.CreatedAt, 'Type': getuser.Type,
                        'LastPastTime': getuser.LastPastTime, 'QQ': getuser.QQ, 'WeChat': getuser.WeChat,
                        'IMToken': getuser.IMToken}
            data = {'SaleId': book.SaleId, 'UserId': book.UserId, 'BookName': book.BookName,
                    'Author': book.Author, 'Classify': book.Classify, 'Publish': book.Publish,
                    'IsSale': book.IsSale, 'Location': book.Location, 'NewPrice': NewPrice,
                    'OldOrNew': book.OldOrNew, 'OldPrice': book.OldPrice, 'Remark': book.Remark,
                    'Tel': book.Tel, 'Count': book.Count, 'isOffLine': book.isOffLine,
                    'Label': book.Label, 'CreatedAt': book.CreatedAt, 'PicList': book.PicList,
                    'Isbn': book.Isbn, 'SchoolName': book.SchoolName, 'ShopId': book.ShopId,
                    'Belong': book.Belong, 'User': userdata}
            newlist.append(data)
        return jsonify({'Message': '成功', 'Data': newlist})
    else:
        return jsonify({'Message': '失败', 'Data': '没有更多数据了'})


# *****************************求   购*****************************
class Buy(db.Model):
    # 共计11项
    __tablename__ = 'buy'
    # ID
    BuyId = db.Column(db.Integer, primary_key=True)
    # 用户ID
    UserId = db.Column(db.Integer)
    # 书名
    BookName = db.Column(db.String)
    # 作者
    Author = db.Column(db.String)
    # 是否已购
    IsBuy = db.Column(db.Boolean)
    # 价格
    Price = db.Column(db.DECIMAL)
    # 备注
    Remark = db.Column(db.String)
    # 发布时间
    CreatedAt = db.Column(db.BIGINT)
    # 电话号
    Tel = db.Column(db.String)
    # 面交
    isOffLine = db.Column(db.Boolean)
    # 地址
    Location = db.Column(db.String)
    # 图片
    Pic = db.Column(db.String)

    def __int__(self, BuyId, UserId, BookName, Author, IsBuy, Price, Remark, CreatedAt, Tel, Location, isOffLine, Pic):
        self.BuyId = BuyId
        self.UserId = UserId
        self.BookName = BookName
        self.Author = Author
        self.IsBuy = IsBuy
        self.Price = Price
        self.Remark = Remark
        self.CreatedAt = CreatedAt
        self.Tel = Tel
        self.Location = Location
        self.isOffLine = isOffLine
        self.Pic = Pic

    def __repr__(self):
        return ''


# 新建求购
@main.route('/api/bookinfo/create/buy', methods=['POST'])
def CreateBuy():
    s = Buy(UserId=request.json['UserId'])
    s.BookName = request.json['BookName']
    s.Author = request.json['Author']
    s.IsBuy = request.json['IsBuy']
    s.CreatedAt = request.json['CreatedAt']
    s.Price = request.json['Price']
    s.Tel = request.json['Tel']
    s.Remark = request.json['Remark']
    s.Location = request.json['Location']
    s.isOffLine = request.json['isOffLine']
    s.Pic = request.json['Pic']
    session.add(s)
    session.commit()
    session.close()
    return jsonify({'Message': '成功', 'Data': '发布成功'})


# 查询求购
@main.route('/api/bookinfo/find/buy', methods=['POST'])
def FindAllBuy():
    skip = request.json['Skip']
    limit = request.json['Limit']
    buylist = Buy.query.order_by(
        desc(Buy.BuyId)).limit(limit).offset(skip).all()
    if buylist:
        newlist = list()
        for buy in buylist:
            Price = str(buy.Price)
            getuser = User.query.filter_by(UserId=buy.UserId).first()
            money = str(getuser.Money)
            userdata = {'UserId': getuser.UserId, 'TelPhone': getuser.TelPhone, 'NickName': getuser.NickName,
                        'SchoolName': getuser.SchoolName, 'Major': getuser.Major, 'Education': getuser.Education,
                        'Sign': getuser.Sign, 'Avatar': getuser.Avatar, 'IsBan': getuser.IsBan,
                        'IsPublish': getuser.IsPublish, 'IsDevelop': getuser.IsDevelop, 'Money': money,
                        'Ex': getuser.Ex, 'Gold': getuser.Gold, 'LastLoginTime': getuser.LastLoginTime,
                        'PassWord': getuser.PassWord, 'Location': getuser.Location,
                        'CreatedAt': getuser.CreatedAt, 'Type': getuser.Type,
                        'LastPastTime': getuser.LastPastTime, 'QQ': getuser.QQ, 'WeChat': getuser.WeChat,
                        'IMToken': getuser.IMToken}
            data = {'BuyId': buy.BuyId, 'UserId': buy.UserId, 'BookName': buy.BookName,
                    'Author': buy.Author, 'IsBuy': buy.IsBuy, 'Price': Price,
                    'Remark': buy.Remark, 'CreatedAt': buy.CreatedAt, 'Tel': buy.Tel,
                    'Location': buy.Location, 'isOffLine': buy.isOffLine, 'User': userdata, 'Pic': buy.Pic}
            newlist.append(data)
        return jsonify({'Message': '成功', 'Data': newlist})
    else:
        return jsonify({'Message': '失败', 'Data': '没有更多数据了'})


# 更新求购
@main.route('/api/bookinfo/update/buy', methods=['POST'])
def UpdateBuy():
    s = Buy(BuyId=request.json['BuyId'])
    s.IsBuy = request.json['IsBuy']
    s.Price = request.json['Price']
    session.merge(s)
    session.commit()
    session.close()
    return jsonify({'Message': '成功', 'Data': '设置成功'})


# *****************************订单*****************************
class Order(db.Model):
    # 共计11项
    __tablename__ = 'order'
    # ID
    OrderId = db.Column(db.Integer, primary_key=True)
    # 类型（出售成交，求购成交）
    # 0为出售 1为求购
    Type = db.Column(db.INTEGER)
    # 卖方ID
    FirstId = db.Column(db.INTEGER)
    # 买方ID
    SecondId = db.Column(db.INTEGER)
    # 书目ID
    BookId = db.Column(db.INTEGER)
    # 成交价
    Price = db.Column(db.DECIMAL)
    # 交易状态
    # 0为未付款 1为已付款 2为已发货 3是已收货 4为取消订单
    State = db.Column(db.INTEGER)
    # 快递单号
    Number = db.Column(db.String)
    # 创建时间
    CreatedAt = db.Column(db.BIGINT)
    # 收获地址
    Location = db.Column(db.String)
    # 备注
    Remark = db.Column(db.String)

    def __int__(self, OrderId, Type, FirstId, SecondId, BookId, Price, State, Number, CreatedAt, Location, Remark):
        self.OrderId = OrderId
        self.Type = Type
        self.FirstId = FirstId
        self.SecondId = SecondId
        self.BookId = BookId
        self.Price = Price
        self.State = State
        self.Number = Number
        self.CreatedAt = CreatedAt
        self.Location = Location
        self.Remark = Remark

    def __repr__(self):
        return ''


# 创建订单
@main.route('/api/orderinfo/create', methods=['POST'])
def CreateOrder():
    s = Order(Type=request.json['Type'])
    s.FirstId = request.json['FirstId']
    s.SecondId = request.json['SecondId']
    s.BookId = request.json['BookId']
    s.State = request.json['State']
    s.CreatedAt = request.json['CreatedAt']
    s.Price = request.json['Price']
    s.Remark = request.json['Remark']
    s.Number = request.json['Number']
    s.Location = request.json['Location']
    session.add(s)
    session.commit()
    session.close()
    return jsonify({'Message': '成功', 'Data': '下单成功'})


# 更新订单
@main.route('/api/orderinfo/update', methods=['POST'])
def UpdateOrder():
    s = Order(OrderId=request.json['OrderId'])
    s.Price = request.json['Price']
    s.State = request.json['State']
    session.merge(s)
    session.commit()
    session.close()
    return jsonify({'Message': '成功', 'Data': '更新成功'})


# *****************************留言*****************************
class Comment(db.Model):
    __tablename__ = 'comment'
    # ID
    CommentId = db.Column(db.Integer, primary_key=True)
    # 留言者
    UserId = db.Column(db.Integer)
    # 被留言id（书的id）
    ToId = db.Column(db.Integer)
    # 回复id,无回复为0
    BackId = db.Column(db.Integer)
    # 内容
    Content = db.Column(db.String)
    # 创建时间
    CreatedAt = db.Column(db.BIGINT)

    def __int__(self, CommentId, BackId, UserId, ToId, Content, CreatedAt):
        self.CommentId = CommentId
        self.BackId = BackId
        self.UserId = UserId
        self.ToId = ToId
        self.Content = Content
        self.CreatedAt = CreatedAt

    def __repr__(self):
        return ''


# 创建留言
@main.route('/api/commentinfo/create', methods=['POST'])
def CreateComment():
    s = Comment(UserId=request.json['UserId'])
    s.ToId = request.json['ToId']
    s.Content = request.json['Content']
    s.CreatedAt = request.json['CreatedAt']
    s.BackId = request.json['BackId']
    session.add(s)
    session.commit()
    session.close()
    return jsonify({'Message': '成功', 'Data': '留言成功'})


# 查询留言
@main.route('/api/commentinfo/find', methods=['POST'])
def FindComment():
    id = request.json['ToId']
    skip = request.json['Skip']
    limit = request.json['Limit']
    commentlist = Comment.query.filter_by(ToId=id).order_by(
        desc(Comment.CommentId)).limit(limit).offset(skip).all()
    if commentlist:
        newlist = list()
        for comment in commentlist:
            getuser = User.query.filter_by(UserId=comment.UserId).first()
            money = str(getuser.Money)
            userdata = {'UserId': getuser.UserId, 'TelPhone': getuser.TelPhone, 'NickName': getuser.NickName,
                        'SchoolName': getuser.SchoolName, 'Major': getuser.Major, 'Education': getuser.Education,
                        'Sign': getuser.Sign, 'Avatar': getuser.Avatar, 'IsBan': getuser.IsBan,
                        'IsPublish': getuser.IsPublish, 'IsDevelop': getuser.IsDevelop, 'Money': money,
                        'Ex': getuser.Ex, 'Gold': getuser.Gold, 'LastLoginTime': getuser.LastLoginTime,
                        'PassWord': getuser.PassWord, 'Location': getuser.Location,
                        'CreatedAt': getuser.CreatedAt, 'Type': getuser.Type,
                        'LastPastTime': getuser.LastPastTime, 'QQ': getuser.QQ, 'WeChat': getuser.WeChat,
                        'IMToken': getuser.IMToken}
            if comment.BackId == 0:
                data = {'CommentId': comment.CommentId, 'UserId': comment.UserId, 'BackId': comment.BackId,
                        'ToId': comment.ToId,
                        'Content': comment.Content,
                        'CreatedAt': comment.CreatedAt, 'User': userdata, 'BackUser': ''}
            else:
                backuser = User.query.filter_by(UserId=comment.BackId).first()
                backmoney = str(backuser.Money)
                backuserdata = {'UserId': backuser.UserId, 'TelPhone': backuser.TelPhone, 'NickName': backuser.NickName,
                                'SchoolName': backuser.SchoolName, 'Major': backuser.Major,
                                'Education': backuser.Education,
                                'Sign': backuser.Sign, 'Avatar': backuser.Avatar, 'IsBan': backuser.IsBan,
                                'IsPublish': backuser.IsPublish, 'IsDevelop': backuser.IsDevelop, 'Money': backmoney,
                                'Ex': backuser.Ex, 'Gold': backuser.Gold, 'LastLoginTime': backuser.LastLoginTime,
                                'PassWord': backuser.PassWord, 'Location': backuser.Location,
                                'CreatedAt': backuser.CreatedAt, 'Type': backuser.Type,
                                'LastPastTime': backuser.LastPastTime, 'QQ': backuser.QQ, 'WeChat': backuser.WeChat,
                                'IMToken': getuser.IMToken}
                data = {'CommentId': comment.CommentId, 'UserId': comment.UserId, 'BackId': comment.BackId,
                        'ToId': comment.ToId,
                        'Content': comment.Content,
                        'CreatedAt': comment.CreatedAt, 'User': userdata, 'BackUser': backuserdata}
            newlist.append(data)
        return jsonify({'Message': '成功', 'Data': newlist})
    else:
        return jsonify({'Message': '失败', 'Data': '没有更多数据了'})


# *****************************关注和被关注*****************************
class StarPeople(db.Model):
    __tablename__ = 'starpeople'
    # ID
    StarPeopleId = db.Column(db.Integer, primary_key=True)
    FirstId = db.Column(db.Integer)
    ToId = db.Column(db.Integer)

    def __int__(self, StarPeopleId, FirstId, ToId):
        self.StarPeopleId = StarPeopleId
        self.FirstId = FirstId
        self.ToId = ToId

    def __repr__(self):
        return ''


# *****************************收藏帖子*****************************
class StarBook(db.Model):
    __tablename__ = 'starbook'
    # ID
    StarBookId = db.Column(db.Integer, primary_key=True)
    FirstId = db.Column(db.Integer)
    ToId = db.Column(db.Integer)

    def __int__(self, StarBookId, FirstId, ToId):
        self.StarBookId = StarBookId
        self.FirstId = FirstId
        self.ToId = ToId

    def __repr__(self):
        return ''


# *****************************购物车*****************************
class Shopping(db.Model):
    __tablename__ = 'shopping'
    # ID
    ShoppingId = db.Column(db.Integer, primary_key=True)
    FirstId = db.Column(db.Integer)
    ToId = db.Column(db.Integer)
    Count = db.Column(db.Integer)

    def __int__(self, ShoppingId, FirstId, ToId, Count):
        self.ShoppingId = ShoppingId
        self.FirstId = FirstId
        self.ToId = ToId
        self.Count = Count

    def __repr__(self):
        return ''


# 加入购物车
@main.route('/api/shoppinginfo/create', methods=['POST'])
def addShopping():
    firstId = request.json['FirstId']
    toId = request.json['ToId']
    mcount = request.json['Count']
    shop = Shopping.query.filter(and_(Shopping.FirstId == firstId, Shopping.ToId == toId)).first()
    if shop:
        s = Shopping(FirstId=firstId)
        s.ToId = toId
        s.Count = mcount
        session.merge(s)
        session.commit()
        session.close()
        return jsonify({'Message': '成功', 'Data': '添加成功'})
    else:
        s = Shopping(FirstId=firstId)
        s.ToId = toId
        s.Count = mcount
        session.add(s)
        session.commit()
        session.close()
        return jsonify({'Message': '成功', 'Data': '添加成功'})


# 更新购物车
@main.route('/api/shoppinginfo/update', methods=['POST'])
def updateShopping():
    s = Shopping(ShoppingId=request.json['ShoppingId'])
    s.Count = request.json['Count']
    session.merge(s)
    session.commit()
    session.close()
    return jsonify({'Message': '成功', 'Data': '更新成功'})


# 删除购物车
@main.route('/api/shoppinginfo/delete', methods=['POST'])
def deleteShopping():
    firstId = request.json['FirstId']
    toId = request.json['ToId']
    Shopping.query.filter(and_(Shopping.FirstId == firstId, Shopping.ToId == toId)).delete()
    return jsonify({'Message': '成功', 'Data': '删除成功'})


# 查询购物车数量（只支持本人查询）
@main.route('/api/shoppinginfo/count', methods=['POST'])
def findShoppingCount():
    firstId = request.json['FirstId']
    count = Shopping.query.filter(Shopping.FirstId == firstId).count()
    return jsonify({'Message': '成功', 'Data': count})


# 查询购物车（只支持本人查询）
@main.route('/api/shoppinginfo/find', methods=['POST'])
def findShopping():
    firstId = request.json['FirstId']
    skip = request.json['Skip']
    limit = request.json['Limit']
    shoppinglist = Shopping.query.filter(Shopping.FirstId == firstId).order_by(
        desc(Shopping.ShoppingId)).limit(limit).offset(skip).all()
    if shoppinglist:
        newlist = list()
        for shop in shoppinglist:
            book = Sale.query.filter_by(SaleId=shop.ToId).order_by(
                desc(Sale.SaleId)).first()
            NewPrice = str(book.NewPrice)
            getuser = User.query.filter_by(UserId=book.UserId).first()
            money = str(getuser.Money)
            userdata = {'UserId': getuser.UserId, 'TelPhone': getuser.TelPhone, 'NickName': getuser.NickName,
                        'SchoolName': getuser.SchoolName, 'Major': getuser.Major, 'Education': getuser.Education,
                        'Sign': getuser.Sign, 'Avatar': getuser.Avatar, 'IsBan': getuser.IsBan,
                        'IsPublish': getuser.IsPublish, 'IsDevelop': getuser.IsDevelop, 'Money': money,
                        'Ex': getuser.Ex, 'Gold': getuser.Gold, 'LastLoginTime': getuser.LastLoginTime,
                        'PassWord': getuser.PassWord, 'Location': getuser.Location,
                        'CreatedAt': getuser.CreatedAt, 'Type': getuser.Type,
                        'LastPastTime': getuser.LastPastTime, 'QQ': getuser.QQ, 'WeChat': getuser.WeChat,
                        'IMToken': getuser.IMToken}
            saledata = {'SaleId': book.SaleId, 'UserId': book.UserId, 'BookName': book.BookName,
                        'Author': book.Author, 'Classify': book.Classify, 'Publish': book.Publish,
                        'IsSale': book.IsSale, 'Location': book.Location, 'NewPrice': NewPrice,
                        'OldOrNew': book.OldOrNew, 'OldPrice': book.OldPrice, 'Remark': book.Remark,
                        'Tel': book.Tel, 'Count': book.Count, 'isOffLine': book.isOffLine,
                        'Label': book.Label, 'CreatedAt': book.CreatedAt, 'PicList': book.PicList,
                        'Isbn': book.Isbn, 'SchoolName': book.SchoolName, 'ShopId': book.ShopId,
                        'Belong': book.Belong, 'User': userdata}
            data = {'FirstId': firstId, 'ShoppingId': shop.ShoppingId, 'ToId': book.SaleId, 'Count': shop.Count,
                    'Sale': saledata}
            newlist.append(data)
        return jsonify({'Message': '成功', 'Data': newlist})
    else:
        return jsonify({'Message': '失败', 'Data': '没有更多数据了'})


# *****************************用户操作*****************************
# 关注
@main.route('/api/starinfo/starpeople/create', methods=['POST'])
def addStarPeople():
    firstId = request.json['FirstId']
    toId = request.json['ToId']
    s = StarPeople(FirstId=firstId)
    s.ToId = toId
    session.add(s)
    session.commit()
    session.close()
    return jsonify({'Message': '成功', 'Data': '关注成功'})


# 收藏
@main.route('/api/starinfo/starbook/create', methods=['POST'])
def addStarBook():
    firstId = request.json['FirstId']
    toId = request.json['ToId']
    s = StarBook(FirstId=firstId)
    s.ToId = toId
    session.add(s)
    session.commit()
    session.close()
    return jsonify({'Message': '成功', 'Data': '收藏成功'})


# 取消关注
@main.route('/api/starinfo/starpeople/delete', methods=['POST'])
def deleteStarPeople():
    firstId = request.json['FirstId']
    toId = request.json['ToId']
    StarPeople.query.filter(and_(StarPeople.FirstId == firstId, StarPeople.ToId == toId)).delete()
    return jsonify({'Message': '成功', 'Data': '取消成功'})


# 取消收藏
@main.route('/api/starinfo/starbook/delete', methods=['POST'])
def deleteStarBook():
    firstId = request.json['FirstId']
    toId = request.json['ToId']
    StarBook.query.filter(and_(StarBook.FirstId == firstId, StarBook.ToId == toId)).delete()
    return jsonify({'Message': '成功', 'Data': '取消成功'})


# 查询是否收藏
@main.route('/api/starinfo/starbook/isstar', methods=['POST'])
def isStarBook():
    firstId = request.json['FirstId']
    toId = request.json['ToId']
    bookList = StarBook.query.filter(and_(StarBook.FirstId == firstId, StarBook.ToId == toId)).all()
    if bookList:
        return jsonify({'Message': '成功', 'Data': '已收藏'})
    else:
        return jsonify({'Message': '成功', 'Data': '未收藏'})


# 查询是否关注
@main.route('/api/starinfo/starpeople/isstar', methods=['POST'])
def isStarPeople():
    firstId = request.json['FirstId']
    toId = request.json['ToId']
    peopleList = StarPeople.query.filter(and_(StarPeople.FirstId == firstId, StarPeople.ToId == toId)).all()
    if peopleList:
        return jsonify({'Message': '成功', 'Data': '已关注'})
    else:
        return jsonify({'Message': '成功', 'Data': '未关注'})


# *****************************用户查寻相关*****************************
# 根据用户id查询出售
@main.route('/api/bookinfo/find/sale/userid', methods=['POST'])
def FindSaleById():
    userid = request.json['UserId']
    skip = request.json['Skip']
    limit = request.json['Limit']
    booklist = Sale.query.filter(Sale.UserId == userid).order_by(
        desc(Sale.SaleId)).limit(limit).offset(skip).all()
    if booklist:
        newlist = list()
        for book in booklist:
            getuser = User.query.filter_by(UserId=book.UserId).first()
            money = str(getuser.Money)
            userdata = {'UserId': getuser.UserId, 'TelPhone': getuser.TelPhone, 'NickName': getuser.NickName,
                        'SchoolName': getuser.SchoolName, 'Major': getuser.Major, 'Education': getuser.Education,
                        'Sign': getuser.Sign, 'Avatar': getuser.Avatar, 'IsBan': getuser.IsBan,
                        'IsPublish': getuser.IsPublish, 'IsDevelop': getuser.IsDevelop, 'Money': money,
                        'Ex': getuser.Ex, 'Gold': getuser.Gold, 'LastLoginTime': getuser.LastLoginTime,
                        'PassWord': getuser.PassWord, 'Location': getuser.Location,
                        'CreatedAt': getuser.CreatedAt, 'Type': getuser.Type,
                        'LastPastTime': getuser.LastPastTime, 'QQ': getuser.QQ, 'WeChat': getuser.WeChat,
                        'IMToken': getuser.IMToken}
            NewPrice = str(book.NewPrice)
            data = {'SaleId': book.SaleId, 'UserId': book.UserId, 'BookName': book.BookName,
                    'Author': book.Author, 'Classify': book.Classify, 'Publish': book.Publish,
                    'IsSale': book.IsSale, 'Location': book.Location, 'NewPrice': NewPrice,
                    'OldOrNew': book.OldOrNew, 'OldPrice': book.OldPrice, 'Remark': book.Remark,
                    'Tel': book.Tel, 'Count': book.Count, 'isOffLine': book.isOffLine,
                    'Label': book.Label, 'CreatedAt': book.CreatedAt, 'PicList': book.PicList,
                    'Isbn': book.Isbn, 'SchoolName': book.SchoolName, 'ShopId': book.ShopId,
                    'Belong': book.Belong, 'User': userdata}
            newlist.append(data)
        return jsonify({'Message': '成功', 'Data': newlist})
    else:
        return jsonify({'Message': '失败', 'Data': '没有更多数据了'})


# 根据用户id查询求购
@main.route('/api/bookinfo/find/buy/userid', methods=['POST'])
def FindBuyById():
    userid = request.json['UserId']
    skip = request.json['Skip']
    limit = request.json['Limit']
    buylist = Buy.query.filter(Buy.UserId == userid).order_by(
        desc(Buy.BuyId)).limit(limit).offset(skip).all()
    if buylist:
        newlist = list()
        for buy in buylist:
            getuser = User.query.filter_by(UserId=buy.UserId).first()
            money = str(getuser.Money)
            userdata = {'UserId': getuser.UserId, 'TelPhone': getuser.TelPhone, 'NickName': getuser.NickName,
                        'SchoolName': getuser.SchoolName, 'Major': getuser.Major, 'Education': getuser.Education,
                        'Sign': getuser.Sign, 'Avatar': getuser.Avatar, 'IsBan': getuser.IsBan,
                        'IsPublish': getuser.IsPublish, 'IsDevelop': getuser.IsDevelop, 'Money': money,
                        'Ex': getuser.Ex, 'Gold': getuser.Gold, 'LastLoginTime': getuser.LastLoginTime,
                        'PassWord': getuser.PassWord, 'Location': getuser.Location,
                        'CreatedAt': getuser.CreatedAt, 'Type': getuser.Type,
                        'LastPastTime': getuser.LastPastTime, 'QQ': getuser.QQ, 'WeChat': getuser.WeChat,
                        'IMToken': getuser.IMToken}
            Price = str(buy.Price)
            data = {'BuyId': buy.BuyId, 'UserId': buy.UserId, 'BookName': buy.BookName,
                    'Author': buy.Author, 'IsBuy': buy.IsBuy, 'Price': Price,
                    'Remark': buy.Remark, 'CreatedAt': buy.CreatedAt, 'Tel': buy.Tel, 'isOffLine': buy.isOffLine,
                    'Location': buy.Location, 'User': userdata, 'Pic': buy.Pic}
            newlist.append(data)
        return jsonify({'Message': '成功', 'Data': newlist})

    else:
        return jsonify({'Message': '失败', 'Data': '没有更多数据了'})


# 根据id查询用户订单
@main.route('/api/orderinfo/find/userid', methods=['POST'])
def FindOrderById():
    userid = request.json['UserId']
    skip = request.json['Skip']
    limit = request.json['Limit']
    type = request.json['Type']
    # 0是我的出售订单，1是我的求购订单
    if type == 0:
        orderList = Order.query.filter(Order.FirstId.like(userid)).order_by(
            desc(Order.OrderId)).limit(limit).offset(skip).all()
    else:
        orderList = Order.query.filter(Order.SecondId.like(userid)).order_by(
            desc(Order.OrderId)).limit(limit).offset(skip).all()
    if orderList:
        newlist = list()
        for order in orderList:
            Price = str(order.Price)
            if order.Type == 0:
                book = Sale.query.filter(Sale.SaleId == order.BookId).order_by(
                    desc(Sale.SaleId)).first()
                NewPrice = str(book.NewPrice)
                bookuser = User.query.filter_by(UserId=book.UserId).first()
                bookusermoney = str(bookuser.Money)
                userdata = {'UserId': bookuser.UserId, 'TelPhone': bookuser.TelPhone, 'NickName': bookuser.NickName,
                            'SchoolName': bookuser.SchoolName, 'Major': bookuser.Major, 'Education': bookuser.Education,
                            'Sign': bookuser.Sign, 'Avatar': bookuser.Avatar, 'IsBan': bookuser.IsBan,
                            'IsPublish': bookuser.IsPublish, 'IsDevelop': bookuser.IsDevelop, 'Money': bookusermoney,
                            'Ex': bookuser.Ex, 'Gold': bookuser.Gold, 'LastLoginTime': bookuser.LastLoginTime,
                            'PassWord': bookuser.PassWord, 'Location': bookuser.Location,
                            'CreatedAt': bookuser.CreatedAt, 'Type': bookuser.Type,
                            'LastPastTime': bookuser.LastPastTime, 'QQ': bookuser.QQ, 'WeChat': bookuser.WeChat,
                            'IMToken': bookuser.IMToken}
                bookdata = {'SaleId': book.SaleId, 'UserId': book.UserId,
                            'BookName': book.BookName,
                            'Author': book.Author, 'Classify': book.Classify,
                            'Publish': book.Publish,
                            'IsSale': book.IsSale, 'Location': book.Location,
                            'NewPrice': NewPrice,
                            'OldOrNew': book.OldOrNew, 'OldPrice': book.OldPrice,
                            'Remark': book.Remark,
                            'Tel': book.Tel,
                            'Label': book.Label, 'CreatedAt': book.CreatedAt,
                            'PicList': book.PicList,
                            'Isbn': book.Isbn, 'SchoolName': book.SchoolName, 'User': userdata}
                firstuser = User.query.filter_by(UserId=order.FirstId).first()
                firstusermoney = str(firstuser.Money)
                firstuserdata = {'UserId': firstuser.UserId, 'TelPhone': firstuser.TelPhone,
                                 'NickName': firstuser.NickName,
                                 'SchoolName': firstuser.SchoolName, 'Major': firstuser.Major,
                                 'Education': firstuser.Education,
                                 'Sign': firstuser.Sign, 'Avatar': firstuser.Avatar, 'IsBan': firstuser.IsBan,
                                 'IsPublish': firstuser.IsPublish, 'IsDevelop': firstuser.IsDevelop,
                                 'Money': firstusermoney,
                                 'Ex': firstuser.Ex, 'Gold': firstuser.Gold, 'LastLoginTime': firstuser.LastLoginTime,
                                 'PassWord': firstuser.PassWord, 'Location': firstuser.Location,
                                 'CreatedAt': firstuser.CreatedAt, 'Type': firstuser.Type,
                                 'LastPastTime': firstuser.LastPastTime, 'QQ': firstuser.QQ, 'WeChat': firstuser.WeChat,
                                 'IMToken': firstuser.IMToken}
                seconduser = User.query.filter_by(UserId=order.SecondId).first()
                secondusermoney = str(seconduser.Money)
                seconduserdata = {'UserId': seconduser.UserId, 'TelPhone': seconduser.TelPhone,
                                  'NickName': seconduser.NickName,
                                  'SchoolName': seconduser.SchoolName, 'Major': seconduser.Major,
                                  'Education': seconduser.Education,
                                  'Sign': seconduser.Sign, 'Avatar': seconduser.Avatar, 'IsBan': seconduser.IsBan,
                                  'IsPublish': seconduser.IsPublish, 'IsDevelop': seconduser.IsDevelop,
                                  'Money': secondusermoney,
                                  'Ex': seconduser.Ex, 'Gold': seconduser.Gold,
                                  'LastLoginTime': seconduser.LastLoginTime,
                                  'PassWord': seconduser.PassWord, 'Location': seconduser.Location,
                                  'CreatedAt': seconduser.CreatedAt, 'Type': seconduser.Type,
                                  'LastPastTime': seconduser.LastPastTime, 'QQ': seconduser.QQ,
                                  'WeChat': seconduser.WeChat, 'IMToken': seconduser.IMToken}
                data = {'OrderId': order.OrderId, 'Type': order.Type, 'FirstId': order.FirstId,
                        'SecondId': order.SecondId,
                        'BookId': order.BookId,
                        'Price': Price, 'State': order.State, 'Number': order.Number, 'CreatedAt': order.CreatedAt,
                        'Location': order.Location,
                        'Remark': order.Remark, 'Book': bookdata, 'FirstUser': firstuserdata,
                        'SecondUser': seconduserdata
                        }
            else:
                book = Buy.query.filter(Buy.BuyId == order.BookId).order_by(
                    desc(Buy.BuyId)).first()
                NewPrice = str(book.Price)
                bookuser = User.query.filter_by(UserId=book.UserId).first()
                bookusermoney = str(bookuser.Money)
                userdata = {'UserId': bookuser.UserId, 'TelPhone': bookuser.TelPhone, 'NickName': bookuser.NickName,
                            'SchoolName': bookuser.SchoolName, 'Major': bookuser.Major, 'Education': bookuser.Education,
                            'Sign': bookuser.Sign, 'Avatar': bookuser.Avatar, 'IsBan': bookuser.IsBan,
                            'IsPublish': bookuser.IsPublish, 'IsDevelop': bookuser.IsDevelop, 'Money': bookusermoney,
                            'Ex': bookuser.Ex, 'Gold': bookuser.Gold, 'LastLoginTime': bookuser.LastLoginTime,
                            'PassWord': bookuser.PassWord, 'Location': bookuser.Location,
                            'CreatedAt': bookuser.CreatedAt, 'Type': bookuser.Type,
                            'LastPastTime': bookuser.LastPastTime, 'QQ': bookuser.QQ, 'WeChat': bookuser.WeChat,
                            'IMToken': bookuser.IMToken}
                bookdata = {'BuyId': book.BuyId, 'UserId': book.UserId,
                            'BookName': book.BookName,
                            'Author': book.Author, 'IsBuy': book.IsBuy, 'Price': NewPrice,
                            'Remark': book.Remark, 'CreatedAt': book.CreatedAt,
                            'Tel': book.Tel,
                            'Location': book.Location, 'User': userdata, 'Pic': book.Pic}
                firstuser = User.query.filter_by(UserId=order.FirstId).first()
                firstusermoney = str(firstuser.Money)
                firstuserdata = {'UserId': firstuser.UserId, 'TelPhone': firstuser.TelPhone,
                                 'NickName': firstuser.NickName,
                                 'SchoolName': firstuser.SchoolName, 'Major': firstuser.Major,
                                 'Education': firstuser.Education,
                                 'Sign': firstuser.Sign, 'Avatar': firstuser.Avatar, 'IsBan': firstuser.IsBan,
                                 'IsPublish': firstuser.IsPublish, 'IsDevelop': firstuser.IsDevelop,
                                 'Money': firstusermoney,
                                 'Ex': firstuser.Ex, 'Gold': firstuser.Gold, 'LastLoginTime': firstuser.LastLoginTime,
                                 'PassWord': firstuser.PassWord, 'Location': firstuser.Location,
                                 'CreatedAt': firstuser.CreatedAt, 'Type': firstuser.Type,
                                 'LastPastTime': firstuser.LastPastTime, 'QQ': firstuser.QQ, 'WeChat': firstuser.WeChat,
                                 'IMToken': firstuser.IMToken}
                seconduser = User.query.filter_by(UserId=order.SecondId).first()
                secondusermoney = str(seconduser.Money)
                seconduserdata = {'UserId': seconduser.UserId, 'TelPhone': seconduser.TelPhone,
                                  'NickName': seconduser.NickName,
                                  'SchoolName': seconduser.SchoolName, 'Major': seconduser.Major,
                                  'Education': seconduser.Education,
                                  'Sign': seconduser.Sign, 'Avatar': seconduser.Avatar, 'IsBan': seconduser.IsBan,
                                  'IsPublish': seconduser.IsPublish, 'IsDevelop': seconduser.IsDevelop,
                                  'Money': secondusermoney,
                                  'Ex': seconduser.Ex, 'Gold': seconduser.Gold,
                                  'LastLoginTime': seconduser.LastLoginTime,
                                  'PassWord': seconduser.PassWord, 'Location': seconduser.Location,
                                  'CreatedAt': seconduser.CreatedAt, 'Type': seconduser.Type,
                                  'LastPastTime': seconduser.LastPastTime, 'QQ': seconduser.QQ,
                                  'WeChat': seconduser.WeChat, 'IMToken': seconduser.IMToken}
                data = {'OrderId': order.OrderId, 'Type': order.Type, 'FirstId': order.FirstId,
                        'SecondId': order.SecondId,
                        'BookId': order.BookId,
                        'Price': Price, 'State': order.State, 'Number': order.Number, 'CreatedAt': order.CreatedAt,
                        'Location': order.Location,
                        'Remark': order.Remark, 'Book': bookdata, 'FirstUser': firstuserdata,
                        'SecondUser': seconduserdata
                        }
            newlist.append(data)
        return jsonify({'Message': '成功', 'Data': newlist})
    else:
        return jsonify({'Message': '失败', 'Data': '没有更多数据了'})


# 关注的人
@main.route('/api/starinfo/starpeople/find/userid', methods=['POST'])
def FindStarPeople():
    userid = request.json['UserId']
    skip = request.json['Skip']
    limit = request.json['Limit']
    userIdList = StarPeople.query.filter(StarPeople.FirstId == userid).limit(limit).offset(skip).all()
    if userIdList:
        newlist = list()
        for userId in userIdList:
            getuser = User.query.filter(User.UserId == userId.ToId).first()
            money = str(getuser.Money)
            data = {'UserId': getuser.UserId, 'TelPhone': getuser.TelPhone, 'NickName': getuser.NickName,
                    'SchoolName': getuser.SchoolName, 'Major': getuser.Major, 'Education': getuser.Education,
                    'Sign': getuser.Sign, 'Avatar': getuser.Avatar, 'IsBan': getuser.IsBan,
                    'IsPublish': getuser.IsPublish, 'IsDevelop': getuser.IsDevelop, 'Money': money,
                    'Ex': getuser.Ex, 'Gold': getuser.Gold, 'LastLoginTime': getuser.LastLoginTime,
                    'PassWord': getuser.PassWord, 'Location': getuser.Location,
                    'CreatedAt': getuser.CreatedAt, 'Type': getuser.Type,
                    'LastPastTime': getuser.LastPastTime, 'QQ': getuser.QQ, 'WeChat': getuser.WeChat,
                    'IMToken': getuser.IMToken}
            newlist.append(data)
        return jsonify(
            {'Message': '成功', 'Data': newlist})
    else:
        return jsonify({'Message': '失败', 'Data': '没有更多数据了'})


# 关注我的人
@main.route('/api/starinfo/staredpeople/find/userid', methods=['POST'])
def FindStaredPeople():
    userid = request.json['UserId']
    skip = request.json['Skip']
    limit = request.json['Limit']
    userIdList = StarPeople.query.filter(StarPeople.ToId == userid).limit(limit).offset(skip).all()
    if userIdList:
        newlist = list()
        for userId in userIdList:
            getuser = User.query.filter(User.UserId == userId.FirstId).first()
            money = str(getuser.Money)
            data = {'UserId': getuser.UserId, 'TelPhone': getuser.TelPhone, 'NickName': getuser.NickName,
                    'SchoolName': getuser.SchoolName, 'Major': getuser.Major, 'Education': getuser.Education,
                    'Sign': getuser.Sign, 'Avatar': getuser.Avatar, 'IsBan': getuser.IsBan,
                    'IsPublish': getuser.IsPublish, 'IsDevelop': getuser.IsDevelop, 'Money': money,
                    'Ex': getuser.Ex, 'Gold': getuser.Gold, 'LastLoginTime': getuser.LastLoginTime,
                    'PassWord': getuser.PassWord, 'Location': getuser.Location,
                    'CreatedAt': getuser.CreatedAt, 'Type': getuser.Type,
                    'LastPastTime': getuser.LastPastTime, 'QQ': getuser.QQ, 'WeChat': getuser.WeChat,
                    'IMToken': getuser.IMToken}
            newlist.append(data)
        return jsonify(
            {'Message': '成功', 'Data': newlist})
    else:
        return jsonify({'Message': '失败', 'Data': '没有更多数据了'})


# 收藏的帖子
@main.route('/api/starinfo/starbook/find/userid', methods=['POST'])
def FindStarBook():
    userid = request.json['UserId']
    skip = request.json['Skip']
    limit = request.json['Limit']
    bookIdList = StarBook.query.filter(StarBook.FirstId == userid).limit(limit).offset(skip).all()
    if bookIdList:
        newlist = list()
        for bookId in bookIdList:
            book = Sale.query.filter(Sale.SaleId == bookId.ToId).first()
            NewPrice = str(book.NewPrice)
            getuser = User.query.filter_by(UserId=book.UserId).first()
            money = str(getuser.Money)
            userdata = {'UserId': getuser.UserId, 'TelPhone': getuser.TelPhone, 'NickName': getuser.NickName,
                        'SchoolName': getuser.SchoolName, 'Major': getuser.Major, 'Education': getuser.Education,
                        'Sign': getuser.Sign, 'Avatar': getuser.Avatar, 'IsBan': getuser.IsBan,
                        'IsPublish': getuser.IsPublish, 'IsDevelop': getuser.IsDevelop, 'Money': money,
                        'Ex': getuser.Ex, 'Gold': getuser.Gold, 'LastLoginTime': getuser.LastLoginTime,
                        'PassWord': getuser.PassWord, 'Location': getuser.Location,
                        'CreatedAt': getuser.CreatedAt, 'Type': getuser.Type,
                        'LastPastTime': getuser.LastPastTime, 'QQ': getuser.QQ, 'WeChat': getuser.WeChat,
                        'IMToken': getuser.IMToken}
            data = {'SaleId': book.SaleId, 'UserId': book.UserId, 'BookName': book.BookName,
                    'Author': book.Author, 'Classify': book.Classify, 'Publish': book.Publish,
                    'IsSale': book.IsSale, 'Location': book.Location, 'NewPrice': NewPrice,
                    'OldOrNew': book.OldOrNew, 'OldPrice': book.OldPrice, 'Remark': book.Remark,
                    'Tel': book.Tel, 'Count': book.Count, 'isOffLine': book.isOffLine,
                    'Label': book.Label, 'CreatedAt': book.CreatedAt, 'PicList': book.PicList,
                    'Isbn': book.Isbn, 'SchoolName': book.SchoolName, 'ShopId': book.ShopId,
                    'Belong': book.Belong, 'User': userdata}
            newlist.append(data)
        return jsonify(
            {'Message': '成功', 'Data': newlist})
    else:
        return jsonify({'Message': '失败', 'Data': '没有更多数据了'})


# 查询求购数目
@main.route('/api/bookinfo/find/buy/<id>', methods=['GET'])
def FindBuyCount(id):
    count = Buy.query.filter(Buy.UserId == id).count()
    return jsonify({'Message': '成功', 'Data': count})


# 查询发布数目
@main.route('/api/bookinfo/find/sale/<id>', methods=['GET'])
def FindSaleCount(id):
    count = Sale.query.filter(Sale.UserId == id).count()
    return jsonify({'Message': '成功', 'Data': count})


# 查询订单数目
@main.route('/api/orderinfo/find/<id>', methods=['GET'])
def FindOrderCount(id):
    count = Order.query.filter(or_(Order.FirstId == id, Order.SecondId == id)).count()
    return jsonify({'Message': '成功', 'Data': count})


# 查询关注数目
@main.route('/api/starinfo/starpeople/find/<id>', methods=['GET'])
def FindStarPeopleCount(id):
    count = StarPeople.query.filter(StarPeople.FirstId == id).count()
    return jsonify({'Message': '成功', 'Data': count})


# 查询被关注数目
@main.route('/api/starinfo/staredpeople/find/<id>', methods=['GET'])
def FindStaredPeopleCount(id):
    count = StarPeople.query.filter(StarPeople.ToId == id).count()
    return jsonify({'Message': '成功', 'Data': count})


# 查询收藏数目
@main.route('/api/starinfo/starbook/find/<id>', methods=['GET'])
def FindStarBookCount(id):
    count = StarBook.query.filter(StarBook.FirstId == id).count()
    return jsonify({'Message': '成功', 'Data': count})


# 查询三种数目
@main.route('/api/allcount/<id>', methods=['GET'])
def GetAllCount(id):
    buyCount = Buy.query.filter(Buy.UserId == id).count()
    saleCount = Sale.query.filter(Sale.UserId == id).count()
    starPeopleCount = StarPeople.query.filter(StarPeople.FirstId == id).count()
    starBookCount = StarBook.query.filter(StarBook.FirstId == id).count()
    data = {'BuyAndSaleCount': buyCount + saleCount, 'StarPeopleCount': starPeopleCount, 'StarBookCount': starBookCount}
    return jsonify({'Message': '成功', 'Data': data})


# ***************************地区/***************************************
# 省份
class Province(db.Model):
    __tablename__ = 'hat_province'
    id = db.Column(db.Integer, primary_key=True)
    provinceID = db.Column(db.String)
    province = db.Column(db.String)

    def __int__(self, id, provinceID, province):
        self.id = id
        self.provinceID = provinceID
        self.province = province

    def __repr__(self):
        return ''


# 城市
class City(db.Model):
    __tablename__ = 'hat_city'
    id = db.Column(db.Integer, primary_key=True)
    cityID = db.Column(db.Integer)
    city = db.Column(db.String)
    father = db.Column(db.String)

    def __int__(self, id, cityID, city, father):
        self.id = id
        self.cityID = cityID
        self.city = city
        self.father = father

    def __repr__(self):
        return ''


# 区
class Area(db.Model):
    __tablename__ = 'hat_area'
    id = db.Column(db.Integer, primary_key=True)
    areaID = db.Column(db.String)
    area = db.Column(db.String)
    father = db.Column(db.String)

    def __int__(self, id, areaID, area, father):
        self.id = id
        self.areaID = areaID
        self.area = area
        self.father = father

    def __repr__(self):
        return ''


# 学校
class School(db.Model):
    __tablename__ = 'tb_school'
    school_id = db.Column(db.Integer, primary_key=True)
    school_name = db.Column(db.String)
    school_type = db.Column(db.Integer)
    area_id = db.Column(db.String)
    area_name = db.Column(db.String)
    display_order = db.Column(db.Integer)

    def __int__(self, school_id, school_name, school_type, area_id, area_name, display_order):
        self.school_id = school_id
        self.school_name = school_name
        self.school_type = school_type
        self.area_id = area_id
        self.area_name = area_name
        self.display_order = display_order

    def __repr__(self):
        return ''


# 获取省份
@main.route('/api/areainfo/province', methods=['GET'])
def GetAllProvince():
    provinceList = Province.query.all()
    newlist = list()
    for province in provinceList:
        newlist.append(province.province)
    return jsonify(
        {'Message': '成功', 'Data': newlist})


# 根据省份获取城市
@main.route('/api/areainfo/city/belong&<province>', methods=['GET'])
def GetCityByProvince(province):
    p = Province.query.filter(Province.province.like(province)).first()
    cityList = City.query.filter(City.father == p.provinceID).all()
    newlist = list()
    for city in cityList:
        newlist.append(city.city)
    return jsonify(
        {'Message': '成功', 'Data': newlist})


# 根据城市获取区
@main.route('/api/areainfo/area/belong&<city>', methods=['GET'])
def GetAreaByCity(city):
    city = City.query.filter(City.city == city).first()
    areaList = Area.query.filter(Area.father == city.cityID).all()
    newlist = list()
    for area in areaList:
        newlist.append(area.area)
    return jsonify(
        {'Message': '成功', 'Data': newlist})


# 根据省份获取学校
@main.route('/api/areainfo/school/belong&<province>', methods=['GET'])
def GetSchoolByProvince(province):
    p = Province.query.filter(Province.province.like(province)).first()
    schoolList = School.query.filter(School.area_name.like(p.province)).all()
    newlist = list()
    for school in schoolList:
        newlist.append(school.school_name)
    return jsonify(
        {'Message': '成功', 'Data': newlist})
