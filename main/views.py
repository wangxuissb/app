# -*- coding: utf-8 -*-
from flask import jsonify, make_response
from . import main

@main.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not Found'}), 404)


@main.route('/', methods=['GET', 'POST'])
def index():
    return '万创科技'