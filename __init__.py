# -*- coding: utf-8 -*-
from flask import Flask, jsonify, request, abort, make_response
import time
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from flask.ext.login import LoginManager, AnonymousUserMixin
from flask.ext.sqlalchemy import SQLAlchemy

databaseurl = 'mysql://root:406726@localhost:3306/eshutao'
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=databaseurl))

db = SQLAlchemy()
login_manager = LoginManager()
session = db.session


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = databaseurl
    app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
    app.config['SECRET_KEY'] = '406726'
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    db.init_app(app)
    login_manager.init_app(app)
    return app
