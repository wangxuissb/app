# -*- coding: utf-8 -*-
from flask import jsonify, make_response
from .. import db_session
from . import main

@main.teardown_request
def shutdown_session(exception=None):
    db_session.remove()


@main.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not Found'}), 404)


@main.route('/', methods=['GET', 'POST'])
def index():
    return '万创科技'