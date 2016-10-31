# -*- coding: utf-8 -*-
from flask import Flask, jsonify, request, abort, make_response
from sqlalchemy import create_engine, MetaData, and_, or_, desc, asc
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
    # 共计20项
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
                Sign, Avatar, IsBan, IsPublish, IsDevelop, Location, Ex, Gold, CreatedAt, LastLoginTime, Type,
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
        self.Money = Money
        self.Ex = Ex
        self.Gold = Gold
        self.Location = Location
        self.CreatedAt = CreatedAt
        self.LastLoginTime = LastLoginTime
        self.Type = Type
        self.LastPastTime = LastPastTime

    def __repr__(self):
        return ''


# 登陆
@main.route('/api/userinfo/login/<Tel>&<Psw>&<Time>', methods=['POST'])
def Login(Tel, Psw, Time):
    get = User.query.filter_by(TelPhone=Tel).first()
    if get is None:
        return jsonify({'Message': '用户不存在', 'Data': ''})
    else:
        if get.PassWord == Psw:
            get.LastLoginTime = Time
            session.merge(get)
            session.commit()
            session.close()
            money = str(get.Money)
            data = {'UserId': get.UserId, 'TelPhone': get.TelPhone, 'NickName': get.NickName,
                    'SchoolName': get.SchoolName, 'Major': get.Major, 'Education': get.Education,
                    'Sign': get.Sign, 'Avatar': get.Avatar, 'IsBan': get.IsBan,
                    'IsPublish': get.IsPublish, 'IsDevelop': get.IsDevelop, 'Money': money,
                    'Ex': get.Ex, 'Gold': get.Gold, 'LastLoginTime': get.LastLoginTime,
                    'PassWord': get.PassWord, 'Location': get.Location,
                    'CreatedAt': get.CreatedAt, 'Type': get.Type,
                    'LastPastTime': get.LastPastTime}
            return jsonify(
                {'Message': '成功', 'Data': data})
        else:
            return jsonify({'Message': '密码错误', 'Data': ''})


# 注册
@main.route('/api/userinfo/signup', methods=['POST'])
def SignUp():
    teluser = User.query.filter_by(TelPhone=request.json['TelPhone']).first()
    if teluser:
        return jsonify({'Message': '手机号码存在'})
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
        u.Location = ''
        u.Shopping = ''
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
    u.Location = request.json['Location']
    u.Type = request.json['Type']
    u.LastPastTime = request.json['LastPastTime']
    session.merge(u)
    session.commit()
    session.close()
    money = str(get.Money)
    get = User.query.filter_by(UserId=request.json['UserId']).first()
    data = {'UserId': u.UserId, 'TelPhone': get.TelPhone, 'NickName': get.NickName,
            'SchoolName': get.SchoolName, 'Major': get.Major, 'Education': get.Education,
            'Sign': get.Sign, 'Avatar': get.Avatar, 'IsBan': get.IsBan,
            'IsPublish': get.IsPublish, 'IsDevelop': get.IsDevelop, 'Money': money,
            'Ex': get.Ex, 'Gold': get.Gold, 'LastLoginTime': get.LastLoginTime,
            'PassWord': get.PassWord, 'Shopping': get.Shopping, 'Location': get.Location,
            'CreatedAt': get.CreatedAt, 'Type': get.Type,
            'LastPastTime': get.LastPastTime}
    return jsonify({'Message': '更新成功', 'Data': data})


# 查找单个用户
@main.route('/api/userinfo/find/<int:Uid>', methods=['GET'])
def FindUserById(Uid):
    get = User.query.filter_by(UserId=Uid).first()
    return jsonify({'UserId': get.UserId, 'TelPhone': get.TelPhone, 'NickName': get.NickName,
                    'SchoolName': get.SchoolName, 'Major': get.Major, 'Education': get.Education,
                    'Sign': get.Sign, 'Avatar': get.Avatar, 'IsBan': get.IsBan,
                    'IsPublish': get.IsPublish, 'IsDevelop': get.IsDevelop, 'Money': money,
                    'Ex': get.Ex, 'Gold': get.Gold, 'LastLoginTime': get.LastLoginTime,
                    'PassWord': get.PassWord, 'Location': get.Location,
                    'CreatedAt': get.CreatedAt, 'Type': get.Type,
                    'LastPastTime': get.LastPastTime})


# *****************************帖子相关*****************************
# *****************************出   售*****************************
class Sale(db.Model):
    # 共计18项
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


def __int__(self, SaleId, UserId, BookName, Author, Classify, Publish, IsSale, Location
            , NewPrice, OldOrNew, OldPrice, Remark, Tel, CreatedAt, PicList
            , Isbn, SchoolName, Label):
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
    s.Label = request.json['Label']
    s.Tel = request.json['Tel']
    s.CreatedAt = request.json['CreatedAt']
    s.PicList = request.json['PicList']
    s.Isbn = request.json['Isbn']
    s.SchoolName = request.json['SchoolName']
    s.Label = request.json['Label']
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
    classify = request.json['Classify']
    issale = request.json['Sale']
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
            data = {'SaleId': book.SaleId, 'UserId': book.UserId, 'BookName': book.BookName,
                    'Author': book.Author, 'Classify': book.Classify, 'Publish': book.Publish,
                    'IsSale': book.IsSale, 'Location': book.Location, 'NewPrice': NewPrice,
                    'OldOrNew': book.OldOrNew, 'OldPrice': book.OldPrice, 'Remark': book.Remark,
                    'Tel': book.Tel,
                    'Label': book.Label, 'CreatedAt': book.CreatedAt, 'PicList': book.PicList,
                    'Isbn': book.Isbn, 'SchoolName': book.SchoolName}
            newlist.append(data)
        return jsonify({'Message': '成功', 'Data': newlist})
    else:
        return jsonify({'Message': '无结果', 'Data': ''})


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
    booklist = Sale.query.filter(or_(Sale.BookName.like("%" + bookname + "%"), Sale.Author.like("%" + bookname + "%"),
                                     Sale.Publish.like("%" + bookname + "%"))).order_by(
        desc(Sale.SaleId)).limit(
        limit).offset(skip).all()
    if booklist:
        newlist = list()
        for book in booklist:
            NewPrice = str(book.NewPrice)
            data = {'SaleId': book.SaleId, 'UserId': book.UserId, 'BookName': book.BookName,
                    'Author': book.Author, 'Classify': book.Classify, 'Publish': book.Publish,
                    'IsSale': book.IsSale, 'Location': book.Location, 'NewPrice': NewPrice,
                    'OldOrNew': book.OldOrNew, 'OldPrice': book.OldPrice, 'Remark': book.Remark,
                    'Tel': book.Tel,
                    'Label': book.Label, 'CreatedAt': book.CreatedAt, 'PicList': book.PicList,
                    'Isbn': book.Isbn, 'SchoolName': book.SchoolName}
            newlist.append(data)
        return jsonify({'Message': '成功', 'Data': newlist})
    else:
        return jsonify({'Message': '无结果', 'Data': ''})


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
    # 地址
    Location = db.Column(db.String)

    def __int__(self, BuyId, UserId, BookName, Author, IsBuy, Price, Remark, CreatedAt, Tel, Location):
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
    session.add(s)
    session.commit()
    session.close()
    return jsonify({'Message': '成功'})


# 查询求购
@main.route('/api/bookinfo/find/buy', methods=['POST'])
def FindAllBuy():
    skip = request.json['Skip']
    limit = request.json['Limit']
    buylist = Buy.query.limit(limit).order_by(
        desc(Sale.SaleId)).offset(skip).all()
    if buylist:
        newlist = list()
        for buy in buylist:
            Price = str(buy.Price)
            data = {'BuyId': get.BuyId, 'UserId': get.UserId, 'BookName': get.BookName,
                    'Author': get.Author, 'IsBuy': get.IsBuy, 'Price': Price,
                    'Remark': get.Remark, 'CreatedAt': get.CreatedAt, 'Tel': get.Tel,
                    'Location': get.Location}
            newlist.append(data)
        return jsonify({'Message': '成功', 'Data': newlist})
    else:
        return jsonify({'Message': '无结果', 'Data': ''})


# 更新求购
# 当前版本只许更改是否已购买
@main.route('/api/bookinfo/update/buy', methods=['POST'])
def UpdateBuy():
    s = Buy(BuyId=request.json['BuyId'])
    s.IsSale = request.json['IsBuy']
    session.merge(s)
    session.commit()
    session.close()
    return jsonify({'Message': '成功'})


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
    s.State = 0
    s.CreatedAt = request.json['CreatedAt']
    s.Price = request.json['Price']
    s.Remark = request.json['Remark']
    s.Number = request.json['Number']
    s.Location = request.json['Location']
    session.add(s)
    session.commit()
    session.close()
    return jsonify({'Message': '成功'})


# 更新订单
@main.route('/api/orderinfo/update', methods=['POST'])
def UpdateOrder():
    s = Order(OrderId=request.json['OrderId'])
    s.Price = request.json['Price']
    s.State = request.json['State']
    session.merge(s)
    session.commit()
    session.close()
    return jsonify({'Message': '成功'})


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
    return jsonify({'Message': '成功'})


# 查询留言
@main.route('/api/commentinfo/find', methods=['POST'])
def FindComment():
    id = request.json['ToId']
    skip = request.json['Skip']
    limit = request.json['Limit']
    commentlist = Comment.query.filter_by(Comment.ToId.like(id)).order_by(
        desc(Sale.SaleId)).limit(limit).offset(skip).all()
    if commentlist:
        newlist = list()
        for comment in commentlist:
            data = {'CommentId': comment.CommentId, 'UserId': comment.UserId, 'BackId': comment.BackId,
                    'ToId': comment.ToId,
                    'Content': comment.Content,
                    'CreatedAt': comment.CreatedAt}
            newlist.append(data)
        return jsonify({'Message': '无结果', 'Data': newlist})
    else:
        return jsonify({'Message': '无结果', 'Data': ''})


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

    def __int__(self, ShoppingId, FirstId, ToId):
        self.ShoppingId = ShoppingId
        self.FirstId = FirstId
        self.ToId = ToId

    def __repr__(self):
        return ''


# *****************************用户操作*****************************
# 关注
@main.route('/api/starinfo/starpeople/create', methods=['POST'])
def addStarPeople():
    firstId = request.json['FirstId']
    toId = request.json['ToId']
    s = StarPeople(StarPeople.FirstId == firstId)
    s.ToId = toId
    session.add(s)
    session.commit()
    session.close()
    return jsonify({'Message': '成功'})


# 收藏
@main.route('/api/starinfo/starbook/create', methods=['POST'])
def addStarBook():
    firstId = request.json['FirstId']
    toId = request.json['ToId']
    s = StarBook(StarPeople.FirstId == firstId)
    s.ToId = toId
    session.add(s)
    session.commit()
    session.close()
    return jsonify({'Message': '成功'})


# 取消关注
@main.route('/api/starinfo/starpeople/delete', methods=['POST'])
def deleteStarPeople():
    firstId = request.json['FirstId']
    toId = request.json['ToId']
    StarPeople.query.filter_by(and_(StarPeople.FirstId.like(firstId), StarPeople.ToId.like(toId))).delete()
    return jsonify({'Message': '成功'})


# 取消收藏
@main.route('/api/starinfo/starbook/delete', methods=['POST'])
def deleteStarBook():
    firstId = request.json['FirstId']
    toId = request.json['ToId']
    StarBook.query.filter_by(and_(StarBook.FirstId.like(firstId), StarBook.ToId.like(toId))).delete()
    return jsonify({'Message': '成功'})


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
            NewPrice = str(book.NewPrice)
            data = {'SaleId': book.SaleId, 'UserId': book.UserId, 'BookName': book.BookName,
                    'Author': book.Author, 'Classify': book.Classify, 'Publish': book.Publish,
                    'IsSale': book.IsSale, 'Location': book.Location, 'NewPrice': NewPrice,
                    'OldOrNew': book.OldOrNew, 'OldPrice': book.OldPrice, 'Remark': book.Remark,
                    'Tel': book.Tel,
                    'Label': book.Label, 'CreatedAt': book.CreatedAt, 'PicList': book.PicList,
                    'Isbn': book.Isbn, 'SchoolName': book.SchoolName}
            newlist.append(data)
        return jsonify({'Message': '成功', 'Data': newlist})
    else:
        return jsonify({'Message': '无结果', 'Data': ''})


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
            Price = str(buy.Price)
            data = {'BuyId': get.BuyId, 'UserId': get.UserId, 'BookName': get.BookName,
                    'Author': get.Author, 'IsBuy': get.IsBuy, 'Price': Price,
                    'Remark': get.Remark, 'CreatedAt': get.CreatedAt, 'Tel': get.Tel,
                    'Location': get.Location}
            newlist.append(data)
        return jsonify({'Message': '成功', 'Data': newlist})

    else:
        return jsonify({'Message': '无结果', 'Data': ''})


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
            data = {'OrderId': order.OrderId, 'Type': order.Type, 'FirstId': order.FirstId,
                    'SecondId': order.SecondId,
                    'BookId': order.BookId,
                    'Price': Price, 'State': order.State, 'Number': order.Number, 'CreatedAt': order.CreatedAt,
                    'Location': order.Location,
                    'Remark': order.Remark}
            newlist.append(data)
        return jsonify({'Message': '成功', 'Data': newlist})
    else:
        return jsonify({'Message': '无结果', 'Data': ''})


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
            get = User.query.filter(User.UserId == userId.ToId).first()
            money = str(get.Money)
            data = {'UserId': get.UserId, 'TelPhone': get.TelPhone, 'NickName': get.NickName,
                    'SchoolName': get.SchoolName, 'Major': get.Major, 'Education': get.Education,
                    'Sign': get.Sign, 'Avatar': get.Avatar, 'IsBan': get.IsBan,
                    'IsPublish': get.IsPublish, 'IsDevelop': get.IsDevelop, 'Money': money,
                    'Ex': get.Ex, 'Gold': get.Gold, 'LastLoginTime': get.LastLoginTime,
                    'PassWord': get.PassWord, 'Location': get.Location,
                    'CreatedAt': get.CreatedAt, 'Type': get.Type,
                    'LastPastTime': get.LastPastTime}
            newlist.append(data)
        return jsonify(
            {'Message': '成功', 'Data': newlist})
    else:
        return jsonify({'Message': '无结果', 'Data': ''})


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
            get = User.query.filter(User.UserId == userId.FirstId).first()
            money = str(get.Money)
            data = {'UserId': get.UserId, 'TelPhone': get.TelPhone, 'NickName': get.NickName,
                    'SchoolName': get.SchoolName, 'Major': get.Major, 'Education': get.Education,
                    'Sign': get.Sign, 'Avatar': get.Avatar, 'IsBan': get.IsBan,
                    'IsPublish': get.IsPublish, 'IsDevelop': get.IsDevelop, 'Money': money,
                    'Ex': get.Ex, 'Gold': get.Gold, 'LastLoginTime': get.LastLoginTime,
                    'PassWord': get.PassWord, 'Location': get.Location,
                    'CreatedAt': get.CreatedAt, 'Type': get.Type,
                    'LastPastTime': get.LastPastTime}
            newlist.append(data)
        return jsonify(
            {'Message': '成功', 'Data': newlist})
    else:
        return jsonify({'Message': '无结果', 'Data': ''})


# 收藏的帖子
@main.route('/api/starinfo/starbiik/find/userid', methods=['POST'])
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
            data = {'SaleId': book.SaleId, 'UserId': book.UserId, 'BookName': book.BookName,
                    'Author': book.Author, 'Classify': book.Classify, 'Publish': book.Publish,
                    'IsSale': book.IsSale, 'Location': book.Location, 'NewPrice': NewPrice,
                    'OldOrNew': book.OldOrNew, 'OldPrice': book.OldPrice, 'Remark': book.Remark,
                    'Tel': book.Tel,
                    'Label': book.Label, 'CreatedAt': book.CreatedAt, 'PicList': book.PicList,
                    'Isbn': book.Isbn, 'SchoolName': book.SchoolName}
            newlist.append(data)
        return jsonify(
            {'Message': '成功', 'Data': newlist})
    else:
        return jsonify({'Message': '无结果', 'Data': ''})


# 查询求购数目
@main.route('/api/bookinfo/find/buy/<id>', methods=['GET'])
def FindBuyCount(id):
    count = Buy.query.filter(Buy.UserId == id).count()
    return jsonify({'Message': '无结果', 'Data': count})


# 查询发布数目
@main.route('/api/bookinfo/find/sale/<id>', methods=['GET'])
def FindSaleCount(id):
    count = Sale.query.filter(Sale.UserId == id).count()
    return jsonify({'Message': '无结果', 'Data': count})


# 查询订单数目
@main.route('/api/orderinfo/find/<id>', methods=['GET'])
def FindOrderCount(id):
    count = Order.query.filter(or_(Order.FirstId == id, Order.SecondId == id)).count()
    return jsonify({'Message': '无结果', 'Data': count})


# 查询关注数目
@main.route('/api/starinfo/starpeople/find/<id>', methods=['GET'])
def FindStarPeopleCount(id):
    count = StarPeople.query.filter(StarPeople.FirstId == id).count()
    return jsonify({'Message': '无结果', 'Data': count})


# 查询被关注数目
@main.route('/api/starinfo/staredpeople/find/<id>', methods=['GET'])
def FindStaredPeopleCount(id):
    count = StarPeople.query.filter(StarPeople.ToId == id).count()
    return jsonify({'Message': '无结果', 'Data': count})
