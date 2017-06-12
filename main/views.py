# -*- coding: utf-8 -*-
import hashlib
import random
import requests
from flask import Flask, jsonify, request, abort, make_response
from flask.ext.login import AnonymousUserMixin, login_user
from sqlalchemy import create_engine, MetaData, and_, or_, desc, asc
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from flask.ext.sqlalchemy import SQLAlchemy
from .. import db, db_session, session, login_manager
from . import main
import json, time, urllib2
import pingpp
from pingpp import Charge

pingpp.api_key = 'sk_live_vz5808mDmvfPXfPKGOqPyfPK'
appid = 'app_fjPKqPGCm980qT8G'
UserIdNum = [0]
login_manager.session_protection = "strong"


@main.teardown_request
def shutdown_session(exception=None):
    db_session.remove()


@main.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not Found'}), 404)


@main.route('/', methods=['GET', 'POST'])
def index():
    return 'e书淘'


# **********************************快递查询***************************
@main.route('/posinfo/find/type=<type>&id=<id>', methods=['GET'])
def PostFind(type, id):
    url = 'http://www.kuaidi100.com/query?type=' + type + '&postid=' + id
    r = requests.get(url)
    j = r.json().get('data')
    return jsonify({'Message': '成功', 'Data': j})


@main.route('/posinfo/getkey', methods=['GET'])
def PostKey():
    return jsonify({'Message': '成功', 'Data': {'Time': 'time', 'Context': 'context'}})


# *******************************支付**********************************
@main.route('/api/chargeinfo/getcharge', methods=['POST'])
def getCharge():
    ch = Charge.create(
        order_no=request.json['OrderNo'],
        amount=request.json['Price'],
        app=dict(id=appid),
        channel=request.json['Channel'],
        currency='cny',
        client_ip='127.0.0.1',
        subject=request.json['Subject'],
        body=request.json['Body'],
    )
    result = ch.to_str()
    j = json.loads(result)
    s = Order(OrderId=request.json['OrderId'])
    s.ChargeId = j['id']
    session.merge(s)
    session.commit()
    session.close()
    return result


# 提现
class Money(db.Model):
    __tablename__ = 'money'
    MoneyId = db.Column(db.Integer, primary_key=True)
    Type = db.Column(db.String)
    UserId = db.Column(db.INTEGER)
    Money = db.Column(db.DECIMAL)
    Name = db.Column(db.String)
    State = db.Column(db.INTEGER)  # 0等待#1完成
    Number = db.Column(db.String)  # 微信号，支付宝号
    Time = db.Column(db.BIGINT)

    def __int__(self, MoneyId, Type, UserId, Money, State, Number, Name, Time):
        self.MoneyId = MoneyId
        self.Type = Type
        self.UserId = UserId
        self.Money = Money
        self.State = State
        self.Number = Number
        self.Name = Name
        self.Time = Time

    def __repr__(self):
        return ''


# 申请提现
@main.route('/api/moneyinfo/get', methods=['POST'])
def getMoney():
    get = User.query.filter_by(UserId=request.json['UserId']).first()
    if get.PassWord == request.json['Psw']:
        user = User(UserId=get.UserId)
        user.Money = float(get.Money) - request.json['Money']
        session.merge(user)
        session.commit()
        session.close()
        money = Money(UserId=request.json['UserId'])
        money.Type = request.json['Type']
        money.Money = request.json['Money']
        money.State = request.json['State']
        money.Number = request.json['Number']
        money.Name = request.json['Name']
        money.Time = request.json['Time']
        session.add(money)
        session.commit()
        session.close()
        return jsonify({'Message': '成功', 'Data': ''})
    else:
        return jsonify({'Message': '失败', 'Data': '密码错误'})


# 查询提现记录
@main.route('/api/moneyinfo/find/', methods=['GET'])
def findMoney():
    id = request.args.get('UserId')
    skip = request.args.get('Skip')
    limit = request.args.get('Limit')
    moneylist = Money.query.filter(Money.UserId == id).order_by(
        desc(Money.MoneyId)).limit(limit).offset(skip).all()
    if moneylist:
        newlist = list()
        for money in moneylist:
            newlist.append(GetMoneyJson(money))
        return jsonify({'Message': '成功', 'Data': newlist})
    else:
        return jsonify({'Message': '失败', 'Data': '没有提现记录'})


# ******************************公众号同步内容****************************
class EMessage(db.Model):
    __tablename__ = 'emessage'
    EMessageId = db.Column(db.Integer, primary_key=True)
    Title = db.Column(db.String)
    Content = db.Column(db.String)
    Data = db.Column(db.String)
    Image = db.Column(db.String)
    Url = db.Column(db.String)

    def __int__(self, EMessageId, Title, Content, Data, Image, Url):
        self.EMessageId = EMessageId
        self.Title = Title
        self.Content = Content
        self.Data = Data
        self.Image = Image
        self.Url = Url

    def __repr__(self):
        return ''


@main.route('/api/emessageinfo/find/', methods=['GET'])
def GetEMessage():
    skip = request.args.get('Skip')
    limit = request.args.get('Limit')
    e = EMessage.query.filter().order_by(
        desc(EMessage.EMessageId)).limit(limit).offset(skip).all()
    if e:
        data = list()
        for message in e:
            data.append(GetEMessageJson(message))
        return jsonify({'Message': '成功', 'Data': data})
    else:
        return jsonify({'Message': '失败', 'Data': '没有数据了'})


def GetEMessageJson(message):
    return {'EMessageId': message.EMessageId, 'Title': message.Title, 'Content': message.Content,
            'Data': message.Data, 'Image': message.Image, 'Url': message.Url}


# *****************************意见反馈*********************************
class FeedBack(db.Model):
    __tablename__ = 'feedback'
    FeedBackId = db.Column(db.Integer, primary_key=True)
    Content = db.Column(db.String)
    UserId = db.Column(db.Integer)
    CreatedAt = db.Column(db.BIGINT)

    def __int__(self, FeedBackId, Content, UserId, CreatedAt):
        self.FeedBackId = FeedBackId
        self.Content = Content
        self.UserId = UserId
        self.CreatedAt = CreatedAt

    def __repr__(self):
        return ''


@main.route('/api/feedbackinfo/create', methods=['POST'])
def CreateFeedBack():
    u = FeedBack(UserId=request.json['UserId'])
    u.Content = request.json['Content']
    u.CreatedAt = request.json['CreatedAt']
    session.add(u)
    session.commit()
    session.close()
    return jsonify({'Message': '成功', 'Data': '反馈成功'})


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
@main.route('/api/appinfo/state/', methods=['GET'])
def getAppState():
    app = App.query.filter(App.Type.like(request.args.get('version'))).first()
    if app:
        return jsonify({'Message': '成功', 'Data': app.State})
    else:
        return jsonify({'Message': '成功', 'Data': '2'})


# 获取主页推荐
@main.route('/api/appinfo/foryou', methods=['GET'])
def getForYou():
    foryoulist = list()
    booklist2 = App.query.filter(App.Type.like('推荐')).all()
    if booklist2:
        for app in booklist2:
            book2 = Sale.query.filter_by(SaleId=app.Content).first()
            data2 = GetSaleJson(book2)
            foryoulist.append(data2)
        return jsonify({'Message': '成功', 'Data': foryoulist})
    else:
        return jsonify({'Message': '失败', 'Data': ''})


@main.route('/api/appinfo/image', methods=['GET'])
def getImage():
    image = App.query.filter(App.Type.like('首页图')).first()
    if image:
        return jsonify({'Message': '成功', 'Data': image.Content})
    else:
        return jsonify({'Message': '失败', 'Data': ''})


# *****************************轮播图*****************************
class Banner(db.Model):
    __tablename__ = 'banner'
    BannerId = db.Column(db.Integer, primary_key=True)
    Url = db.Column(db.String)
    Click = db.Column(db.Boolean)
    Pic = db.Column(db.String)

    def __int__(self, BannerId, Url, Click, Pic):
        self.BannerId = BannerId
        self.Url = Url
        self.Click = Click
        self.Pic = Pic

    def __repr__(self):
        return ''


@main.route('/api/bannerinfo/get', methods=['GET'])
def getBanner():
    blist = list()
    bannerList = Banner.query.filter().all()
    if bannerList:
        for banner in bannerList:
            blist.append(GetBannerJson(banner))
        return jsonify({'Message': '成功', 'Data': blist})
    else:
        return jsonify({'Message': '失败', 'Data': ''})


def GetBannerJson(banner):
    return {'BannerId': banner.BannerId, 'Url': banner.Url, 'Click': banner.Click, 'Pic': banner.Pic}


# *****************************用户相关*****************************
class User(db.Model):
    # 共计23项
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
    # 店铺Id
    ShopId = db.Column(db.Integer)

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

    def __int__(self, UserId, TelPhone, PassWord, NickName, SchoolName, Major, Education,
                Sign, Avatar, IsBan, IsPublish, IsDevelop, Location, Ex, Gold, CreatedAt, LastLoginTime, Type,
                LastPastTime, Money, QQ, WeChat, ShopId):
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
        self.ShopId = ShopId

    def __repr__(self):
        return ''

    def is_authenticated(self):
        """Check the user whether logged in."""

        # Check the User's instance whether Class AnonymousUserMixin's instance.
        if isinstance(self, AnonymousUserMixin):
            return False
        else:
            return True

    def is_active(self):
        """Check the user whether pass the activation process."""
        return True

    def is_anonymous(self):
        """Check the user's login status whether is anonymous."""
        if isinstance(self, AnonymousUserMixin):
            return True
        else:
            return False

    def get_id(self):
        """Get the user's uuid from database."""
        return unicode(self.UserId)


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(UserId=int(user_id)).first()


# 登陆
@main.route('/api/userinfo/login', methods=['POST'])
def Login():
    Tel = request.json['Tel']
    Psw = request.json['Psw']
    Time = request.json['Time']
    get = User.query.filter_by(TelPhone=Tel).first()
    if get is None:
        return jsonify({'Message': '失败', 'Data': '用户不存在'})
    else:
        if get.PassWord == Psw:
            # IMLogOut(get.UserId)
            u = User(UserId=get.UserId)
            u.LastLoginTime = Time
            session.merge(u)
            session.commit()
            session.close()
            user = User.query.filter_by(TelPhone=Tel).first()
            data = GetUserJson(user)
            login_user(user)
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
        u.ShopId = 0
        u.Location = ''
        u.Shopping = ''
        u.QQ = ''
        u.WeChat = ''
        u.LastPastTime = 0
        session.add(u)
        session.commit()
        session.close()
        user = User.query.filter_by(TelPhone=request.json['TelPhone']).first()
        LoginIM(user.UserId, request.json['PassWord'])
        return jsonify({'Message': '成功', 'Data': '注册成功'})


# 更新资料
@main.route('/api/userinfo/update', methods=['POST'])
def UpdateUser():
    olduser = User.query.filter_by(UserId=request.json['UserId']).first()
    oldpsw = olduser.PassWord
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
    u.ShopId = request.json['ShopId']
    session.merge(u)
    session.commit()
    session.close()
    user = User.query.filter_by(UserId=request.json['UserId']).first()
    data = GetUserJson(user)
    ChangeIM(request.json['UserId'], request.json['PassWord'], oldpsw)
    return jsonify({'Message': '成功', 'Data': data})


# 查找单个用户
@main.route('/api/userinfo/find/', methods=['GET'])
def FindUserById():
    Uid = int(request.args.get('id'))
    user = User.query.filter_by(UserId=Uid).first()
    data = GetUserJson(user)
    return jsonify({'Message': '成功', 'Data': data})


# 手机号查找单个用户
@main.route('/api/userinfo/findbytel/', methods=['GET'])
def FindUserByTel():
    Tel = request.args.get('tel')
    user = User.query.filter_by(TelPhone=Tel).first()
    if user:
        data = GetUserJson(user)
        return jsonify({'Message': '成功', 'Data': data})
    else:
        return jsonify({'Message': '成功', 'Data': '该用户不存在'})


# QQ登陆
@main.route('/api/userinfo/loginbyqq/', methods=['GET'])
def LoginByQQ():
    QQ = request.args.get('qq')
    user = User.query.filter_by(QQ=QQ).first()
    if user:
        data = GetUserJson(user)
        return jsonify({'Message': '成功', 'Data': data})
    else:
        return jsonify({'Message': '失败', 'Data': '该用户不存在'})


# *****************************商家相关*****************************
class Shop(db.Model):
    __tablename__ = 'shop'
    # id
    ShopId = db.Column(db.Integer, primary_key=True)
    # 用户ID
    UserId = db.Column(db.Integer)
    # 商家头像
    Name = db.Column(db.String)
    # 商家名称
    Avatar = db.Column(db.String)
    # 手机号码
    Tel = db.Column(db.String)
    # 地址
    Adress = db.Column(db.String)
    # 公司执照
    Licence = db.Column(db.String)
    # 类型
    Type = db.Column(db.Integer)
    # 负责人姓名
    UserName = db.Column(db.String)
    # 负责人身份证号
    UserCardNumber = db.Column(db.String)
    # 负责人手机号码
    UserTel = db.Column(db.String)
    # 公告
    Content = db.Column(db.String)
    # 封禁
    IsBan = db.Column(db.Boolean)

    # 评分
    Score = db.Column(db.Integer)
    # 评论数
    CommentCount = db.Column(db.Integer)

    # 三个管理员
    Manager1 = db.Column(db.Integer)
    Manager2 = db.Column(db.Integer)
    Manager3 = db.Column(db.Integer)

    def __int__(self, ShopId, UserId, Name, Avatar, Tel, Adress, Licence,
                Type, UserName, UserCardNumber, UserTel, Content, IsBan, Score, CommentCount, Manager1, Manager2,
                Manager3):
        self.ShopId = ShopId
        self.UserId = UserId
        self.Name = Name
        self.Avatar = Avatar
        self.Tel = Tel
        self.Adress = Adress
        self.Licence = Licence
        self.Type = Type
        self.UserName = UserName
        self.UserCardNumber = UserCardNumber
        self.UserTel = UserTel
        self.Content = Content
        self.IsBan = IsBan
        self.Score = Score
        self.CommentCount = CommentCount
        self.Manager1 = Manager1
        self.Manager2 = Manager2
        self.Manager3 = Manager3

    def __repr__(self):
        return ''


# 根据id查询商家
@main.route('/api/shopinfo/find/', methods=['GET'])
def FindShop():
    shop = Shop.query.filter_by(ShopId=request.args.get('id')).first()
    if shop:
        data = GetShopJson(shop)
        return jsonify({'Message': '成功', 'Data': data})
    else:
        return jsonify({'Message': '失败', 'Data': '商家不存在'})


# 查询商家
@main.route('/api/shopinfo/find/all/', methods=['GET'])
def FindAllShop():
    shop = Shop.query.filter_by(IsBan=False).order_by(
        desc(Shop.ShopId)).limit(request.args.get('limit')).offset(request.args.get('skip')).all()
    if shop:
        data = GetShopJson(shop)
        return jsonify({'Message': '成功', 'Data': data})
    else:
        return jsonify({'Message': '失败', 'Data': '商家不存在'})


# 修改商户信息
@main.route('/api/shopinfo/update', methods=['POST'])
def UpdateShop():
    shop = Shop.query.filter_by(ShopId=request.json['ShopId']).first()
    user1 = User(UserId=shop.Manager1)
    user1.ShopId = 0
    session.merge(user1)
    user2 = User(UserId=shop.Manager2)
    user2.ShopId = 0
    user3 = User(UserId=shop.Manager3)
    user3.ShopId = 0
    session.merge(user3)
    shop = Shop(ShopId=request.json['ShopId'])
    shop.Avatar = request.json['Avatar']
    shop.Content = request.json['Content']
    shop.Manager1 = request.json['Manager1']
    shop.Manager2 = request.json['Manager2']
    shop.Manager3 = request.json['Manager3']
    session.merge(shop)
    user1 = User(UserId=request.json['Manager1'])
    user1.ShopId = request.json['ShopId']
    session.merge(user1)
    user2 = User(UserId=request.json['Manager2'])
    user2.ShopId = request.json['ShopId']
    session.merge(user2)
    user3 = User(UserId=request.json['Manager3'])
    user3.ShopId = request.json['ShopId']
    session.merge(user3)
    session.commit()
    session.close()
    return jsonify({'Message': '成功', 'Data': '更新成功'})


class ShopComment(db.Model):
    __tablename__ = 'shop_comment'
    # id
    CommentId = db.Column(db.Integer, primary_key=True)
    # id
    ShopId = db.Column(db.Integer)
    # 用户ID
    UserId = db.Column(db.Integer)
    # 评论
    Content = db.Column(db.String)
    # 评分
    Score = db.Column(db.Integer)
    # 时间
    CreatedAt = db.Column(db.BIGINT)

    def __int__(self, CommentId, ShopId, UserId, Content, Score, CreatedAt):
        self.ShopId = ShopId
        self.UserId = UserId
        self.Content = Content
        self.Score = Score
        self.CreatedAt = CreatedAt
        self.CommentId = CommentId

    def __repr__(self):
        return ''


# 新建评论
@main.route('/api/shopinfo/create/comment', methods=['POST'])
def CreateShopComment():
    comment = ShopComment(ShopId=request.json['ShopId'])
    comment.UserId = request.json['UserId']
    comment.Content = request.json['Content']
    comment.Score = request.json['Score']
    comment.CreatedAt = request.json['CreatedAt']
    session.add(comment)
    shop = Shop.query.filter_by(ShopId=request.json['ShopId']).first()
    s = Shop(ShopId=request.json['ShopId'])
    s.Score = shop.Score + request.json['Score']
    s.CommentCount = shop.CommentCount + 1
    session.merge(s)
    session.commit()
    session.close()
    return jsonify({'Message': '成功', 'Data': '成功'})


# 根据商家id查询评论
@main.route('/api/shopinfo/find/comment/', methods=['GET'])
def FindShopComment():
    shop = ShopComment.query.filter_by(ShopId=request.args.get('id')).order_by(
        desc(ShopComment.CommentId)).limit(request.args.get('limit')).offset(request.args.get('skip')).all()
    if shop:
        data = list()
        for comment in shop:
            data.append(GetShopCommentJson(comment))
        return jsonify({'Message': '成功', 'Data': data})
    else:
        return jsonify({'Message': '失败', 'Data': '暂无评论'})


# 根据商家id查询评论数量
@main.route('/api/shopinfo/count/comment/', methods=['GET'])
def FindShopCommentCount():
    shop = ShopComment.query.filter_by(ShopId=request.args.get('id')).count()
    return jsonify({'Message': '成功', 'Data': shop})


class ShopClassify(db.Model):
    __tablename__ = 'shop_classify'
    # id
    ClassifyId = db.Column(db.Integer, primary_key=True)
    # 用户ID
    ShopId = db.Column(db.Integer)
    # 分类
    Classify = db.Column(db.String)

    def __int__(self, ClassifyId, ShopId, Classify):
        self.ClassifyId = ClassifyId
        self.ShopId = ShopId
        self.Classify = Classify

    def __repr__(self):
        return ''


# 新建分类
@main.route('/api/shopinfo/create/classify', methods=['POST'])
def CreateShopClassify():
    classify = ShopClassify(ShopId=request.json['ShopId'])
    classify.Classify = request.json['Classify']
    session.add(classify)
    session.commit()
    session.close()
    return jsonify({'Message': '成功', 'Data': '成功'})


# 删除分类
@main.route('/api/shopinfo/delete/classify', methods=['POST'])
def DeleteShopClassify():
    ShopClassify.query.filter_by(ClassifyId=request.json['ClassifyId']).delete()
    return jsonify({'Message': '成功', 'Data': '成功'})


# 根据商家id查询分类
@main.route('/api/shopinfo/find/classify/', methods=['GET'])
def FindShopClassify():
    shop = ShopClassify.query.filter_by(ShopId=request.args.get('id')).order_by(
        desc(ShopClassify.ClassifyId)).limit(request.args.get('limit')).offset(request.args.get('skip')).all()
    if shop:
        data = list()
        for classify in shop:
            data.append(GetShopClassifyJson(classify))
        return jsonify({'Message': '成功', 'Data': data})
    else:
        return jsonify({'Message': '失败', 'Data': '暂无分类'})


def GetShopClassifyJson(classify):
    return {'ClassifyId': classify.ClassifyId,
            'ShopId': classify.ShopId,
            'Classify': classify.Classify}


class ShopBook(db.Model):
    __tablename__ = 'shop_book'
    # id
    ShopBookId = db.Column(db.Integer, primary_key=True)
    # 用户ID
    ShopId = db.Column(db.Integer)
    # 分类id
    ClassifyId = db.Column(db.Integer)
    # 书的id
    BookId = db.Column(db.Integer)

    def __int__(self, ShopBookId, ShopId, BookId, ClassifyId):
        self.ShopBookId = ShopBookId
        self.ShopId = ShopId
        self.BookId = BookId
        self.ClassifyId = ClassifyId

    def __repr__(self):
        return ''


# 新建分类下的书籍
@main.route('/api/shopinfo/create/book', methods=['POST'])
def CreateShopClassifyBook():
    book = ShopBook(ShopId=request.json['ShopId'])
    book.ClassifyId = request.json['ClassifyId']
    book.BookId = request.json['BookId']
    session.add(book)
    session.commit()
    session.close()
    return jsonify({'Message': '成功', 'Data': '成功'})


# 删除分类书籍
@main.route('/api/shopinfo/delete/book', methods=['POST'])
def DeleteShopClassifyBook():
    ShopBook.query.filter_by(ShopBookId=request.json['ShopBookId']).delete()
    return jsonify({'Message': '成功', 'Data': '成功'})


# 更新分类下的书籍
@main.route('/api/shopinfo/update/book', methods=['POST'])
def UpdateShopClassifyBook():
    book = ShopBook(BookId=request.json['SaleId'])
    book.ClassifyId = request.json['ClassifyId']
    session.merge(book)
    s = Sale(SaleId=request.json['SaleId'])
    s.Count = request.json['Count']
    s.NewPrice = request.json['NewPrice']
    session.merge(s)
    session.commit()
    session.close()
    return jsonify({'Message': '成功', 'Data': '成功'})


# 根据商家id查询分类书籍
@main.route('/api/shopinfo/find/book/', methods=['GET'])
def FindShopClassifyBook():
    classifyId = request.args.get('ClassifyId')
    if (int(classifyId) == 0):
        shop = ShopBook.query.filter(ShopBook.ShopId == request.args.get('ShopId')).order_by(
            desc(ShopBook.ShopBookId)).limit(request.args.get('limit')).offset(request.args.get('skip')).all()
    else:
        shop = ShopBook.query.filter(and_(ShopBook.ShopId == request.args.get('ShopId'),
                                          ShopBook.ClassifyId == classifyId)).order_by(
            desc(ShopBook.ShopBookId)).limit(request.args.get('limit')).offset(request.args.get('skip')).all()
    if shop:
        data = list()
        for book in shop:
            data.append(GetShopBookJson(book))
        return jsonify({'Message': '成功', 'Data': data})
    else:
        return jsonify({'Message': '失败', 'Data': '暂无书籍'})


def GetShopBookJson(book):
    sale = Sale.query.filter_by(SaleId=book.BookId).first()
    classify = ShopClassify.query.filter_by(ClassifyId=book.ClassifyId).first()
    return {'ShopBookId': book.ShopBookId, 'Classify': GetShopClassifyJson(classify),
            'ShopId': book.ShopId, 'Book': GetSaleJson(sale),
            'BookId': book.BookId, 'ClassifyId': book.ClassifyId}


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
    sale = Sale.query.filter(
        and_(Sale.UserId == request.json['UserId'], Sale.BookName == request.json['BookName'])).order_by(
        desc(Sale.SaleId)).first()
    return jsonify({'Message': '成功', 'Data': sale.SaleId})


# 查询出售
# 无序0
# 价钱从低到高10，从高到底11
# 新旧从新到旧20，从旧到新21
# desc降序，asc升序
@main.route('/api/bookinfo/find/sale/', methods=['GET'])
def FindAllSale():
    type = int(request.args.get('type', 0))
    skip = int(request.args.get('skip', 0))
    schoolname = request.args.get('schoolname', '')
    classify = request.args.get('classify', '')
    limit = int(request.args.get('limit', 20))
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
            data = GetSaleJson(book)
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


# 查询剩余数量
@main.route('/api/bookinfo/find/count/', methods=['GET'])
def FindSaleBookCount():
    id = int(request.args.get('id'))
    book = Sale.query.filter(Sale.SaleId == id).first()
    return jsonify({'Message': '成功', 'Data': book.Count})


# 按书名搜索
@main.route('/api/bookinfo/search/sale/bookname/', methods=['GET'])
def FindSaleBookName():
    bookname = request.args.get('bookname')
    skip = int(request.args.get('skip'))
    limit = int(request.args.get('limit'))
    booklist = Sale.query.filter(or_(Sale.BookName.like("%" + bookname + "%"), Sale.Author.like("%" + bookname + "%"),
                                     Sale.Publish.like("%" + bookname + "%"),
                                     Sale.Classify.like("%" + bookname + "%"))).order_by(
        desc(Sale.SaleId)).limit(
        limit).offset(skip).all()
    if booklist:
        newlist = list()
        for book in booklist:
            data = GetSaleJson(book)
            newlist.append(data)
        return jsonify({'Message': '成功', 'Data': newlist})
    else:
        return jsonify({'Message': '失败', 'Data': '没有更多数据了'})


# *****************************求   购*****************************
class Buy(db.Model):
    # 共计12项
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
@main.route('/api/bookinfo/find/buy/', methods=['GET'])
def FindAllBuy():
    skip = int(request.args.get('skip'))
    limit = int(request.args.get('limit'))
    buylist = Buy.query.filter(Buy.IsBuy == False).order_by(
        desc(Buy.BuyId)).limit(limit).offset(skip).all()
    if buylist:
        newlist = list()
        for buy in buylist:
            data = GetBuyJson(buy)
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
    # 共计20项
    __tablename__ = 'order'
    # ID
    OrderId = db.Column(db.Integer, primary_key=True)
    # 类型（出售成交，求购成交）
    # 0为出售 1为求购
    Type = db.Column(db.INTEGER)
    # 数量
    Count = db.Column(db.INTEGER)
    # 卖方ID
    FirstId = db.Column(db.INTEGER)
    # 买方ID
    SecondId = db.Column(db.INTEGER)
    # 书目ID
    BookId = db.Column(db.INTEGER)
    # 成交价
    Price = db.Column(db.DECIMAL)
    # 交易状态
    # 等待卖家确认信息，等待买家确认信息并付款，等待卖家发货，等待买家收获，等待买家卖家确认交易完成
    State = db.Column(db.INTEGER)
    # 配送方式
    SendType = db.Column(db.String)
    # 快递单号
    Number = db.Column(db.String)
    # 快递公司
    PosType = db.Column(db.String)
    # 创建时间
    CreatedAt = db.Column(db.BIGINT)
    # 付款时间
    PayAt = db.Column(db.BIGINT)
    # 发货时间
    SendAt = db.Column(db.BIGINT)
    # 收获时间
    GetAt = db.Column(db.BIGINT)
    # 交易完成时间
    FinishAt = db.Column(db.BIGINT)
    # 收获人
    Peolple = db.Column(db.String)
    # 联系方式
    Tel = db.Column(db.String)
    # 邮编
    SendCode = db.Column(db.String)
    # 收获地址
    Location = db.Column(db.Integer)
    # 备注
    Remark = db.Column(db.String)
    # ping++支付id
    ChargeId = db.Column(db.String)

    def __int__(self, OrderId, Type, FirstId, SecondId, BookId, Price, State, Number, CreatedAt, Location, Remark,
                SendType, Count, PayAt, SendAt, GetAt, FinishAt, Peolple, Tel, SendCode, ChargeId, PosType):
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
        self.SendType = SendType
        self.Count = Count
        self.PayAt = PayAt
        self.GetAt = GetAt
        self.FinishAt = FinishAt
        self.Peolple = Peolple
        self.SendCode = SendCode
        self.Tel = Tel
        self.SendAt = SendAt
        self.ChargeId = ChargeId
        self.PosType = PosType

    def __repr__(self):
        return ''


# 创建订单
@main.route('/api/orderinfo/create', methods=['POST'])
def CreateOrder():
    if request.json['Type'] == 0:
        Shopping.query.filter(
            and_(Shopping.FirstId == request.json['SecondId'], Shopping.ToId == request.json['BookId'])).delete()
        sale = Sale.query.filter(Sale.SaleId == request.json['BookId']).first()
        newcount = sale.Count - request.json['Count']
        if newcount >= 0:
            newsale = Sale(SaleId=sale.SaleId)
            newsale.Count = newcount
            if newcount == 0:
                newsale.IsSale = True
            session.merge(newsale)
            s = Order(Type=request.json['Type'])
            s.PayAt = request.json['PayAt']
            s.GetAt = request.json['GetAt']
            s.FinishAt = request.json['FinishAt']
            s.Peolple = request.json['Peolple']
            s.SendCode = request.json['SendCode']
            s.SendAt = request.json['SendAt']
            s.Tel = request.json['Tel']
            s.FirstId = request.json['FirstId']
            s.SecondId = request.json['SecondId']
            s.BookId = request.json['BookId']
            s.State = request.json['State']
            s.CreatedAt = request.json['CreatedAt']
            s.Price = request.json['Price']
            s.Remark = request.json['Remark']
            s.Number = request.json['Number']
            s.Location = request.json['Location']
            s.SendType = request.json['SendType']
            s.Count = request.json['Count']
            s.PosType = ''
            s.ChargeId = ''
            session.add(s)
            session.commit()
            session.close()
        else:
            return jsonify({'Message': '失败', 'Data': '数量不足'})
    else:
        newbuy = Buy(BuyId=request.json['BookId'])
        newbuy.IsBuy = True
        session.merge(newbuy)
        s = Order(Type=request.json['Type'])
        s.PayAt = request.json['PayAt']
        s.GetAt = request.json['GetAt']
        s.FinishAt = request.json['FinishAt']
        s.Peolple = request.json['Peolple']
        s.SendCode = request.json['SendCode']
        s.SendAt = request.json['SendAt']
        s.Tel = request.json['Tel']
        s.FirstId = request.json['FirstId']
        s.SecondId = request.json['SecondId']
        s.BookId = request.json['BookId']
        s.State = request.json['State']
        s.CreatedAt = request.json['CreatedAt']
        s.Price = request.json['Price']
        s.Remark = request.json['Remark']
        s.Number = request.json['Number']
        s.Location = request.json['Location']
        s.SendType = request.json['SendType']
        s.Count = request.json['Count']
        s.PosType = ''
        s.ChargeId = ''
        session.add(s)
        session.commit()
        session.close()
    return jsonify({'Message': '成功', 'Data': '下单成功'})


# 更新订单
@main.route('/api/orderinfo/update', methods=['POST'])
def UpdateOrder():
    s = Order(OrderId=request.json['OrderId'])
    s.PayAt = request.json['PayAt']
    s.GetAt = request.json['GetAt']
    s.FinishAt = request.json['FinishAt']
    s.Peolple = request.json['Peolple']
    s.SendCode = request.json['SendCode']
    s.SendAt = request.json['SendAt']
    s.Tel = request.json['Tel']
    s.FirstId = request.json['FirstId']
    s.SecondId = request.json['SecondId']
    s.BookId = request.json['BookId']
    s.State = request.json['State']
    s.CreatedAt = request.json['CreatedAt']
    s.Price = request.json['Price']
    s.Remark = request.json['Remark']
    s.Number = request.json['Number']
    s.Location = request.json['Location']
    s.SendType = request.json['SendType']
    s.Count = request.json['Count']
    s.ChargeId = request.json['ChargeId']
    s.PosType = request.json['PosType']
    session.merge(s)
    session.commit()
    session.close()
    if request.json['State'] == 4:
        user = User.query.filter(User.UserId == request.json['FirstId']).first()
        oldMoney = user.Money
        newuser = User(UserId=user.UserId)
        newuser.Money = float(oldMoney) + request.json['Price']
        session.merge(newuser)
        session.commit()
        session.close()
    if request.json['State'] == 5:
        if request.json['Type'] == 0:
            sale = Sale.query.filter(Sale.SaleId == request.json['BookId']).first()
            newcount = sale.Count + request.json['Count']
            newsale = Sale(SaleId=sale.SaleId)
            newsale.IsSale = False
            newsale.Count = newcount
            session.merge(newsale)
            session.commit()
            session.close()
        else:
            newbuy = Buy(BuyId=request.json['BookId'])
            newbuy.IsBuy = False
            session.merge(newbuy)
            session.commit()
            session.close()
    return jsonify({'Message': '成功', 'Data': '更新成功'})


# 删除订单
@main.route('/api/orderinfo/delete', methods=['POST'])
def DeleteOrder():
    Order.query.filter(Order.OrderId == request.json['OrderId']).delete()
    return jsonify({'Message': '成功', 'Data': '删除成功'})


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
@main.route('/api/commentinfo/find/', methods=['GET'])
def FindComment():
    skip = int(request.args.get('skip'))
    id = int(request.args.get('id'))
    limit = int(request.args.get('limit'))
    commentlist = Comment.query.filter_by(ToId=id).order_by(
        desc(Comment.CommentId)).limit(limit).offset(skip).all()
    if commentlist:
        newlist = list()
        for comment in commentlist:
            data = GetCommentJson(comment)
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
@main.route('/api/shoppinginfo/count/', methods=['GET'])
def findShoppingCount():
    id = int(request.args.get('id'))
    count = Shopping.query.filter(Shopping.FirstId == id).count()
    return jsonify({'Message': '成功', 'Data': count})


# 查询购物车（只支持本人查询）
@main.route('/api/shoppinginfo/find/', methods=['GET'])
def findShopping():
    skip = int(request.args.get('skip'))
    id = int(request.args.get('id'))
    limit = int(request.args.get('limit'))
    shoppinglist = Shopping.query.filter(Shopping.FirstId == id).order_by(
        desc(Shopping.ShoppingId)).limit(limit).offset(skip).all()
    if shoppinglist:
        newlist = list()
        for shop in shoppinglist:
            data = GetShoppingJson(shop)
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
@main.route('/api/starinfo/starbook/isstar/', methods=['GET'])
def isStarBook():
    id = int(request.args.get('id'))
    toid = int(request.args.get('toid'))
    bookList = StarBook.query.filter(and_(StarBook.FirstId == id, StarBook.ToId == toid)).all()
    if bookList:
        return jsonify({'Message': '成功', 'Data': '已收藏'})
    else:
        return jsonify({'Message': '成功', 'Data': '未收藏'})


# 查询是否关注
@main.route('/api/starinfo/starpeople/isstar/', methods=['GET'])
def isStarPeople():
    id = int(request.args.get('id'))
    toid = int(request.args.get('toid'))
    peopleList = StarPeople.query.filter(and_(StarPeople.FirstId == id, StarPeople.ToId == toid)).all()
    if peopleList:
        return jsonify({'Message': '成功', 'Data': '已关注'})
    else:
        return jsonify({'Message': '成功', 'Data': '未关注'})


# *****************************用户查寻相关*****************************
# 根据用户id查询出售
@main.route('/api/bookinfo/find/sale/userid/', methods=['GET'])
def FindSaleById():
    skip = int(request.args.get('skip'))
    id = int(request.args.get('id'))
    limit = int(request.args.get('limit'))
    booklist = Sale.query.filter(Sale.UserId == id).order_by(
        desc(Sale.SaleId)).limit(limit).offset(skip).all()
    if booklist:
        newlist = list()
        for book in booklist:
            data = GetSaleJson(book)
            newlist.append(data)
        return jsonify({'Message': '成功', 'Data': newlist})
    else:
        return jsonify({'Message': '失败', 'Data': '没有更多数据了'})


# 根据用户id查询求购
@main.route('/api/bookinfo/find/buy/userid/', methods=['GET'])
def FindBuyById():
    skip = int(request.args.get('skip'))
    id = int(request.args.get('id'))
    limit = int(request.args.get('limit'))
    buylist = Buy.query.filter(Buy.UserId == id).order_by(
        desc(Buy.BuyId)).limit(limit).offset(skip).all()
    if buylist:
        newlist = list()
        for buy in buylist:
            data = GetBuyJson(buy)
            newlist.append(data)
        return jsonify({'Message': '成功', 'Data': newlist})

    else:
        return jsonify({'Message': '失败', 'Data': '没有更多数据了'})


# 根据id查询用户订单
@main.route('/api/orderinfo/find/userid/', methods=['GET'])
def FindOrderById():
    type = int(request.args.get('type'))
    skip = int(request.args.get('skip'))
    id = int(request.args.get('id'))
    state = int(request.args.get('state'))
    limit = int(request.args.get('limit'))
    # 0是我的出售订单，1是我的购买订单
    if type == 0:
        orderList = Order.query.filter(Order.FirstId.like(id), Order.State == state).order_by(
            desc(Order.OrderId)).limit(limit).offset(skip).all()
    else:
        orderList = Order.query.filter(Order.SecondId.like(id), Order.State == state).order_by(
            desc(Order.OrderId)).limit(limit).offset(skip).all()
    if orderList:
        newlist = list()
        for order in orderList:
            data = GetOrderJson(order)
            newlist.append(data)
        return jsonify({'Message': '成功', 'Data': newlist})
    else:
        return jsonify({'Message': '失败', 'Data': '没有更多数据了'})


# 关注的人
@main.route('/api/starinfo/starpeople/find/userid/', methods=['GET'])
def FindStarPeople():
    skip = int(request.args.get('skip'))
    id = int(request.args.get('id'))
    limit = int(request.args.get('limit'))
    userIdList = StarPeople.query.filter(StarPeople.FirstId == id).limit(limit).offset(skip).all()
    if userIdList:
        newlist = list()
        for userId in userIdList:
            getuser = User.query.filter(User.UserId == userId.ToId).first()
            data = GetUserJson(getuser)
            newlist.append(data)
        return jsonify(
            {'Message': '成功', 'Data': newlist})
    else:
        return jsonify({'Message': '失败', 'Data': '没有更多数据了'})


# 关注我的人
@main.route('/api/starinfo/staredpeople/find/userid/', methods=['GET'])
def FindStaredPeople():
    skip = int(request.args.get('skip'))
    id = int(request.args.get('id'))
    limit = int(request.args.get('limit'))
    userIdList = StarPeople.query.filter(StarPeople.ToId == id).limit(limit).offset(skip).all()
    if userIdList:
        newlist = list()
        for userId in userIdList:
            getuser = User.query.filter(User.UserId == userId.FirstId).first()
            data = GetUserJson(getuser)
            newlist.append(data)
        return jsonify(
            {'Message': '成功', 'Data': newlist})
    else:
        return jsonify({'Message': '失败', 'Data': '没有更多数据了'})


# 收藏的帖子
@main.route('/api/starinfo/starbook/find/userid/', methods=['GET'])
def FindStarBook():
    skip = int(request.args.get('skip'))
    id = int(request.args.get('id'))
    limit = int(request.args.get('limit'))
    bookIdList = StarBook.query.filter(StarBook.FirstId == id).limit(limit).offset(skip).all()
    if bookIdList:
        newlist = list()
        for bookId in bookIdList:
            book = Sale.query.filter(Sale.SaleId == bookId.ToId).first()
            data = GetSaleJson(book)
            newlist.append(data)
        return jsonify(
            {'Message': '成功', 'Data': newlist})
    else:
        return jsonify({'Message': '失败', 'Data': '没有更多数据了'})


# 查询求购数目
@main.route('/api/bookinfo/find/buy/count/', methods=['GET'])
def FindBuyCount():
    id = int(request.args.get('id'))
    count = Buy.query.filter(Buy.UserId == id).count()
    return jsonify({'Message': '成功', 'Data': count})


# 查询发布数目
@main.route('/api/bookinfo/find/sale/count/', methods=['GET'])
def FindSaleCount():
    id = int(request.args.get('id'))
    count = Sale.query.filter(Sale.UserId == id).count()
    return jsonify({'Message': '成功', 'Data': count})


# 查询订单数目
@main.route('/api/orderinfo/find/count/', methods=['GET'])
def FindOrderCount():
    id = int(request.args.get('id'))
    count = Order.query.filter(
        and_(or_(Order.FirstId == id, Order.SecondId == id), and_(Order.State != -1, Order.State != -2, ))).count()
    sale = Order.query.filter(
        and_(Order.FirstId == id, and_(Order.State != -1, Order.State != -2, ))).count()
    buy = Order.query.filter(
        and_(Order.SecondId == id, and_(Order.State != -1, Order.State != -2, ))).count()
    return jsonify({'Message': '成功', 'Data': {'Count': count, 'Sale': sale, 'Buy': buy}})


# 查询关注数目
@main.route('/api/starinfo/starpeople/find/count/', methods=['GET'])
def FindStarPeopleCount():
    id = int(request.args.get('id'))
    count = StarPeople.query.filter(StarPeople.FirstId == id).count()
    return jsonify({'Message': '成功', 'Data': count})


# 查询被关注数目
@main.route('/api/starinfo/staredpeople/find/count/', methods=['GET'])
def FindStaredPeopleCount():
    id = int(request.args.get('id'))
    count = StarPeople.query.filter(StarPeople.ToId == id).count()
    return jsonify({'Message': '成功', 'Data': count})


# 查询收藏数目
@main.route('/api/starinfo/starbook/find/count/', methods=['GET'])
def FindStarBookCount():
    id = int(request.args.get('id'))
    count = StarBook.query.filter(StarBook.FirstId == id).count()
    return jsonify({'Message': '成功', 'Data': count})


# 查询三种数目
@main.route('/api/allcount/', methods=['GET'])
def GetAllCount():
    id = int(request.args.get('id'))
    buyCount = Buy.query.filter(Buy.UserId == id).count()
    saleCount = Sale.query.filter(Sale.UserId == id).count()
    starPeopleCount = StarPeople.query.filter(StarPeople.FirstId == id).count()
    starBookCount = StarBook.query.filter(StarBook.FirstId == id).count()
    data = {'BuyAndSaleCount': buyCount + saleCount, 'StarPeopleCount': starPeopleCount, 'StarBookCount': starBookCount}
    return jsonify({'Message': '成功', 'Data': data})


# ***************************地区/***************************************
# 省份
class Province(db.Model):
    __tablename__ = 'location_province'
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
    __tablename__ = 'location_city'
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
    __tablename__ = 'location_area'
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
    __tablename__ = 'location_school'
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
@main.route('/api/areainfo/city/belong&<string:province>', methods=['GET'])
def GetCityByProvince(province):
    p = Province.query.filter(Province.province.like(province)).first()
    cityList = City.query.filter(City.father.like(p.provinceID)).all()
    newlist = list()
    for city in cityList:
        newlist.append(city.city)
    return jsonify(
        {'Message': '成功', 'Data': newlist})


# 根据城市获取区
@main.route('/api/areainfo/area/belong&<string:province>&<string:city>', methods=['GET'])
def GetAreaByCity(province, city):
    p = Province.query.filter(Province.province.like(province)).first()
    city = City.query.filter(and_(City.city.like(city), City.father.like(p.provinceID))).first()
    areaList = Area.query.filter(Area.father.like(city.cityID)).all()
    newlist = list()
    for area in areaList:
        newlist.append(area.area)
    return jsonify(
        {'Message': '成功', 'Data': newlist})


# 根据省份获取学校
@main.route('/api/areainfo/area/belong&<string:province>', methods=['GET'])
def GetSchoolByProvince(province):
    p = Province.query.filter(Province.province.like(province)).first()
    schoolList = School.query.filter(School.area_name.like(p.province)).all()
    newlist = list()
    for school in schoolList:
        newlist.append(school.school_name)
    return jsonify(
        {'Message': '成功', 'Data': newlist})


# ***************************地址***************************************
class Adress(db.Model):
    __tablename__ = 'adress'
    AdressId = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String)
    Tel = db.Column(db.String)
    Area = db.Column(db.String)
    Location = db.Column(db.String)
    Code = db.Column(db.String)
    IsDefault = db.Column(db.Boolean)
    UserId = db.Column(db.Integer)

    def __int__(self, AdressId, Name, Tel, Area, Location, Code, IsDefault, UserId):
        self.AdressId = AdressId
        self.Name = Name
        self.Tel = Tel
        self.Area = Area
        self.Location = Location
        self.Code = Code
        self.IsDefault = IsDefault
        self.UserId = UserId

    def __repr__(self):
        return ''


# 添加地址
@main.route('/api/adressinfo/create', methods=['POST'])
def CreateAdress():
    u = Adress(UserId=request.json['UserId'])
    u.Name = request.json['Name']
    u.Tel = request.json['Tel']
    u.Location = request.json['Location']
    u.Code = request.json['Code']
    u.Area = request.json['Area']
    get = Adress.query.filter(
        and_(Adress.UserId == request.json['UserId'], Adress.IsDefault == True)).first()
    if get:
        u.IsDefault = request.json['IsDefault']
        if request.json['IsDefault']:
            w = Adress(AdressId=get.AdressId)
            w.IsDefault = False
            session.merge(w)
            session.commit()
            session.close()
    else:
        u.IsDefault = True
    session.add(u)
    session.commit()
    session.close()
    return jsonify({'Message': '成功', 'Data': '成功'})


# 查询地址
@main.route('/api/adressinfo/find/', methods=['GET'])
def FindAdress():
    id = int(request.args.get('id'))
    newlist = list()
    get = Adress.query.filter(
        and_(Adress.UserId == id, Adress.IsDefault == True)).first()
    if get:
        getdata = {'Name': get.Name, 'Tel': get.Tel,
                   'Location': get.Location,
                   'Code': get.Code, 'IsDefault': get.IsDefault,
                   'UserId': get.UserId,
                   'AdressId': get.AdressId, 'Area': get.Area}
        newlist.append(getdata)
    get1 = Adress.query.filter(
        and_(Adress.UserId == id, Adress.IsDefault == False)).all()
    if get1:
        for a in get1:
            getdata1 = {'Name': a.Name, 'Tel': a.Tel,
                        'Location': a.Location,
                        'Code': a.Code, 'IsDefault': a.IsDefault,
                        'UserId': a.UserId,
                        'AdressId': a.AdressId, 'Area': a.Area}
            newlist.append(getdata1)
    return jsonify({'Message': '成功', 'Data': newlist})


# 更新地址
@main.route('/api/adressinfo/update', methods=['POST'])
def UpdateAdress():
    u = Adress(AdressId=request.json['AdressId'])
    u.Name = request.json['Name']
    u.Tel = request.json['Tel']
    u.Location = request.json['Location']
    u.Code = request.json['Code']
    u.Area = request.json['Area']
    u.UserId = request.json['UserId']
    u.IsDefault = request.json['IsDefault']
    session.merge(u)
    session.commit()
    session.close()
    # get = Adress.query.filter(
    #     and_(Adress.UserId == request.json['UserId'], Adress.IsDefault == True)).first()
    # if get:
    #     print ''
    # else:
    #     get1 = Adress.query.filter(
    #         and_(Adress.UserId == request.json['UserId'], Adress.IsDefault == False)).first()
    #     if get1:
    #         u = Adress(AdressId=get1.AdressId)
    #         u.IsDefault = True
    #         session.merge(u)
    #         session.commit()
    #         session.close()
    return jsonify({'Message': '成功', 'Data': '设置成功'})


# 删除地址
@main.route('/api/adressinfo/delete', methods=['POST'])
def DeleteAdress():
    Adress.query.filter_by(AdressId=request.json['AdressId']).delete()
    get = Adress.query.filter(
        and_(Adress.UserId == request.json['UserId'], Adress.IsDefault == True)).first()
    if get:
        print ''
    else:
        get1 = Adress.query.filter(
            and_(Adress.UserId == request.json['UserId'], Adress.IsDefault == False)).first()
        if get1:
            u = Adress(AdressId=get1.AdressId)
            u.IsDefault = True
            session.merge(u)
            session.commit()
            session.close()
    return jsonify({'Message': '成功', 'Data': '删除成功'})


# 修改默认地址
@main.route('/api/adressinfo/default', methods=['POST'])
def DefaultAdress():
    get = Adress.query.filter(
        and_(Adress.UserId == request.json['UserId'], Adress.IsDefault == True)).first()
    u = Adress(AdressId=get.AdressId)
    u.IsDefault = False
    session.merge(u)
    session.commit()
    session.close()
    u = Adress(AdressId=request.json['AdressId'])
    u.IsDefault = True
    session.merge(u)
    session.commit()
    session.close()
    return jsonify({'Message': '成功', 'Data': '成功'})


def GetUserJson(user):
    money = str(user.Money)
    return {'UserId': user.UserId, 'TelPhone': user.TelPhone, 'NickName': user.NickName,
            'SchoolName': user.SchoolName, 'Major': user.Major, 'Education': user.Education,
            'Sign': user.Sign, 'Avatar': user.Avatar, 'IsBan': user.IsBan,
            'IsPublish': user.IsPublish, 'IsDevelop': user.IsDevelop, 'Money': money,
            'Ex': user.Ex, 'Gold': user.Gold, 'LastLoginTime': user.LastLoginTime,
            'PassWord': '', 'Location': user.Location,
            'CreatedAt': user.CreatedAt, 'Type': user.Type,
            'LastPastTime': user.LastPastTime, 'QQ': user.QQ, 'WeChat': user.WeChat, 'ShopId': user.ShopId}


def GetSaleJson(sale):
    user = User.query.filter_by(UserId=sale.UserId).first()
    price = str(sale.NewPrice)
    return {'SaleId': sale.SaleId, 'UserId': sale.UserId, 'BookName': sale.BookName,
            'Author': sale.Author, 'Classify': sale.Classify, 'Publish': sale.Publish,
            'IsSale': sale.IsSale, 'Location': sale.Location, 'NewPrice': price,
            'OldOrNew': sale.OldOrNew, 'OldPrice': sale.OldPrice, 'Remark': sale.Remark,
            'Tel': sale.Tel, 'Count': sale.Count, 'isOffLine': sale.isOffLine,
            'Label': sale.Label, 'CreatedAt': sale.CreatedAt, 'PicList': sale.PicList,
            'Isbn': sale.Isbn, 'SchoolName': sale.SchoolName, 'ShopId': sale.ShopId,
            'Belong': sale.Belong, 'User': GetUserJson(user)}


def GetBuyJson(buy):
    user = User.query.filter_by(UserId=buy.UserId).first()
    price = str(buy.Price)
    return {'BuyId': buy.BuyId, 'UserId': buy.UserId, 'BookName': buy.BookName,
            'Author': buy.Author, 'IsBuy': buy.IsBuy, 'Price': price,
            'Remark': buy.Remark, 'CreatedAt': buy.CreatedAt, 'Tel': buy.Tel,
            'Location': buy.Location, 'isOffLine': buy.isOffLine, 'Pic': buy.Pic, 'User': GetUserJson(user)}


def GetCommentJson(comment):
    user = User.query.filter_by(UserId=comment.UserId).first()
    if comment.BackId == 0:
        return {'CommentId': comment.CommentId, 'UserId': comment.UserId, 'BackId': comment.BackId,
                'ToId': comment.ToId,
                'Content': comment.Content,
                'CreatedAt': comment.CreatedAt, 'User': GetUserJson(user), 'BackUser': ''}
    else:
        backuser = User.query.filter_by(UserId=comment.BackId).first()
        return {'CommentId': comment.CommentId, 'UserId': comment.UserId, 'BackId': comment.BackId,
                'ToId': comment.ToId,
                'Content': comment.Content,
                'CreatedAt': comment.CreatedAt, 'User': GetUserJson(user), 'BackUser': GetUserJson(backuser)}


def GetShoppingJson(shopping):
    book = Sale.query.filter_by(SaleId=shopping.ToId).first()
    return {'FirstId': shopping.FirstId, 'ShoppingId': shopping.ShoppingId, 'ToId': shopping.ToId,
            'Count': shopping.Count,
            'Sale': GetSaleJson(book)}


def GetMoneyJson(money):
    m = str(money.Money)
    return {'MoneyId': money.MoneyId, 'Type': money.Type, 'UserId': money.UserId,
            'Money': m,
            'State': money.State, 'Number': money.Number, 'Name': money.Name, 'Time': money.Time}


def GetOrderJson(order):
    price = str(order.Price)
    firstuser = User.query.filter_by(UserId=order.FirstId).first()
    seconduser = User.query.filter_by(UserId=order.SecondId).first()
    if order.Type == 0:
        book = Sale.query.filter(Sale.SaleId == order.BookId).order_by(
            desc(Sale.SaleId)).first()
        return {'OrderId': order.OrderId, 'Type': order.Type, 'FirstId': order.FirstId,
                'SecondId': order.SecondId,
                'BookId': order.BookId,
                'Price': price, 'State': order.State, 'Number': order.Number, 'CreatedAt': order.CreatedAt,
                'Location': order.Location,
                'Remark': order.Remark, 'Book': GetSaleJson(book), 'FirstUser': GetUserJson(firstuser),
                'SecondUser': GetUserJson(seconduser), 'SendType': order.SendType, 'Count': order.Count,
                'PayAt': order.PayAt, 'GetAt': order.GetAt, 'FinishAt': order.FinishAt, 'Peolple': order.Peolple,
                'SendCode': order.SendCode,
                'Tel': order.Tel, 'SendAt': order.SendAt, 'ChargeId': order.ChargeId, 'PosType': order.PosType,
                'Adress': GetAdressJson(order)
                }
    else:
        book = Buy.query.filter(Buy.BuyId == order.BookId).order_by(
            desc(Buy.BuyId)).first()
        return {'OrderId': order.OrderId, 'Type': order.Type, 'FirstId': order.FirstId,
                'SecondId': order.SecondId,
                'BookId': order.BookId,
                'Price': price, 'State': order.State, 'Number': order.Number, 'CreatedAt': order.CreatedAt,
                'Location': order.Location,
                'Remark': order.Remark, 'Book': GetBuyJson(book), 'FirstUser': GetUserJson(firstuser),
                'SecondUser': GetUserJson(seconduser), 'SendType': order.SendType, 'Count': order.Count,
                'PayAt': order.PayAt, 'GetAt': order.GetAt, 'FinishAt': order.FinishAt, 'Peolple': order.Peolple,
                'SendCode': order.SendCode,
                'Tel': order.Tel, 'SendAt': order.SendAt, 'ChargeId': order.ChargeId, 'PosType': order.PosType,
                'Adress': GetAdressJson(order)
                }


def GetAdressJson(order):
    get = Adress.query.filter(Adress.AdressId == order.Location).first()
    if get:
        return {'Name': get.Name, 'Tel': get.Tel,
                'Location': get.Location,
                'Code': get.Code, 'IsDefault': get.IsDefault,
                'UserId': get.UserId,
                'AdressId': get.AdressId, 'Area': get.Area}
    else:
        return {}


def GetShopJson(shop):
    user = User.query.filter_by(UserId=shop.UserId).first()
    user1 = User.query.filter_by(UserId=shop.Manager1).first()
    user2 = User.query.filter_by(UserId=shop.Manager2).first()
    user3 = User.query.filter_by(UserId=shop.Manager3).first()
    classify = ShopClassify.query.filter_by(ShopId=shop.ShopId).order_by(
        desc(ShopClassify.ClassifyId)).all()
    data = list()
    if classify:
        for c in classify:
            data.append(GetShopClassifyJson(c))
    return {'ShopId': shop.ShopId, 'UserId': shop.UserId,
            'Name': shop.Name, 'User': GetUserJson(user), 'Type': shop.Type,
            'Avatar': shop.Avatar, 'Tel': shop.Tel,
            'Adress': shop.Adress, 'Manager1': GetUserJson(user1),
            'Content': shop.Content, 'IsBan': shop.IsBan,
            'Score': shop.Score, 'CommentCount': shop.CommentCount,
            'Manager2': GetUserJson(user2), 'Manager3': GetUserJson(user3), 'ShopClassify': data}


def GetShopCommentJson(comment):
    user = User.query.filter_by(UserId=comment.UserId).first()
    return {'CommentId': comment.CommentId, 'ShopId': comment.ShopId,
            'UserId': comment.UserId, 'User': GetUserJson(user),
            'Content': comment.Content, 'Score': comment.Score, 'CreatedAt': comment.CreatedAt}


def LoginIM(id, psw):
    datainfo = {
        "grant_type": "client_credentials",
        "client_id": "YXA6CGQjYMKIEeaNd20Ttx1Dzg",
        "client_secret": "YXA6wrNShdgwMFWDXcGKvl0yY9AFcuY"
    }
    headers = {
        'content-type': 'application/json;charset=UTF-8'
    }
    r = requests.post("https://a1.easemob.com/1145161215178634/wohuiaini1314/token", data=json.dumps(datainfo),
                      headers=headers)
    token = r.json().get('access_token')
    header = {
        'content-type': 'application/json;charset=UTF-8',
        'Authorization': 'Bearer ' + token
    }
    user = {
        "username": id,
        "password": psw
    }
    r = requests.post("https://a1.easemob.com/1145161215178634/wohuiaini1314/users", data=json.dumps(user),
                      headers=header)


def ChangeIM(id, newpsw, oldpsw):
    datainfo = {
        "grant_type": "client_credentials",
        "client_id": "YXA6CGQjYMKIEeaNd20Ttx1Dzg",
        "client_secret": "YXA6wrNShdgwMFWDXcGKvl0yY9AFcuY"
    }
    headers = {
        'content-type': 'application/json;charset=UTF-8'
    }
    r = requests.post("https://a1.easemob.com/1145161215178634/wohuiaini1314/token", data=json.dumps(datainfo),
                      headers=headers)
    token = r.json().get('access_token')
    datainfo = {
        "newpassword": newpsw,
    }
    headers = {
        'Authorization': 'Bearer ' + token
    }
    r = requests.post("https://a1.easemob.com/1145161215178634/wohuiaini1314/users/" + str(id) + "/password",
                      data=json.dumps(datainfo),
                      headers=headers)


@main.route('/api/iminfo/logout/<int:id>', methods=['POST'])
def IM_LogOut(id):
    datainfo = {
        "grant_type": "client_credentials",
        "client_id": "YXA6CGQjYMKIEeaNd20Ttx1Dzg",
        "client_secret": "YXA6wrNShdgwMFWDXcGKvl0yY9AFcuY"
    }
    headers = {
        'content-type': 'application/json;charset=UTF-8'
    }
    r = requests.post("https://a1.easemob.com/1145161215178634/wohuiaini1314/token", data=json.dumps(datainfo),
                      headers=headers)
    token = r.json().get('access_token')
    headers = {
        'Authorization': 'Bearer ' + token
    }
    r = requests.get(
        "https://a1.easemob.com/1145161215178634/wohuiaini1314/users/" + id + "/disconnect",
        headers=headers)


def IMLogOutById(id):
    datainfo = {
        "grant_type": "client_credentials",
        "client_id": "YXA6CGQjYMKIEeaNd20Ttx1Dzg",
        "client_secret": "YXA6wrNShdgwMFWDXcGKvl0yY9AFcuY"
    }
    headers = {
        'content-type': 'application/json;charset=UTF-8'
    }
    r = requests.post("https://a1.easemob.com/1145161215178634/wohuiaini1314/token", data=json.dumps(datainfo),
                      headers=headers)
    token = r.json().get('access_token')
    headers = {
        'Authorization': 'Bearer ' + token
    }
    r = requests.get(
        "https://a1.easemob.com/1145161215178634/wohuiaini1314/users/" + str(id) + "/disconnect",
        headers=headers)


# UFAN
# 注册
@main.route('/api/ufan/register', methods=['POST'])
def UFANIM():
    id = request.json['id']
    psw = request.json['psw']
    datainfo = {
        "grant_type": "client_credentials",
        "client_id": "YXA68WtU0CKpEee-DHeGrsjOSg",
        "client_secret": "YXA6W814_yeBE_fiIBFJuW2V0gzekrI"
    }
    headers = {
        'content-type': 'application/json;charset=UTF-8'
    }
    r = requests.post("https://a1.easemob.com/1196170416115093/ufan/token", data=json.dumps(datainfo),
                      headers=headers)
    token = r.json().get('access_token')
    header = {
        'content-type': 'application/json;charset=UTF-8',
        'Authorization': 'Bearer ' + token
    }
    user = {
        "username": id,
        "password": psw
    }
    r = requests.post("https://a1.easemob.com/1196170416115093/ufan/users", data=json.dumps(user),
                      headers=header)
    return jsonify(
        {'Message': '成功', 'Data': '注册成功'})


# UFAN
# 改密
@main.route('/api/ufan/changepsw', methods=['POST'])
def UFANCHANGE():
    id = request.json['id']
    psw = request.json['psw']
    datainfo = {
        "grant_type": "client_credentials",
        "client_id": "YXA68WtU0CKpEee-DHeGrsjOSg",
        "client_secret": "YXA6W814_yeBE_fiIBFJuW2V0gzekrI"
    }
    headers = {
        'content-type': 'application/json;charset=UTF-8'
    }
    r = requests.post("https://a1.easemob.com/1196170416115093/ufan/token", data=json.dumps(datainfo),
                      headers=headers)
    token = r.json().get('access_token')
    datainfo = {
        "newpassword": psw,
    }
    headers = {
        'Authorization': 'Bearer ' + token
    }
    r = requests.post("https://a1.easemob.com/1196170416115093/ufan/users/" + str(id) + "/password",
                      data=json.dumps(datainfo),
                      headers=headers)
    return jsonify(
        {'Message': '成功', 'Data': '修改成功'})


# UFAN
# 下线
@main.route('/api/ufan/logout', methods=['POST'])
def UFANLOGOUT():
    id = request.json['id']
    datainfo = {
        "grant_type": "client_credentials",
        "client_id": "YXA68WtU0CKpEee-DHeGrsjOSg",
        "client_secret": "YXA6W814_yeBE_fiIBFJuW2V0gzekrI"
    }
    headers = {
        'content-type': 'application/json;charset=UTF-8'
    }
    r = requests.post("https://a1.easemob.com/1196170416115093/ufan/token", data=json.dumps(datainfo),
                      headers=headers)
    token = r.json().get('access_token')
    headers = {
        'Authorization': 'Bearer ' + token
    }
    r = requests.get(
        "https://a1.easemob.com/1196170416115093/ufan/users/" + str(id) + "/disconnect",
        headers=headers)
    return jsonify(
        {'Message': '成功', 'Data': '下线成功'})
