# -*- coding: utf-8 -*-
import os
import subprocess
from flask import jsonify, make_response, request
from . import main


@main.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not Found'}), 404)


@main.route('/', methods=['GET', 'POST'])
def index():
    return '万创科技'


# ~/cura/CuraEngine2.5 slice -v -p -j ~/cura/resources/definitions/delta.def.json -o ~/cura/output/1.gcode -l ~/cura/models/1.stl
@main.route('/api/model/slice/', methods=['GET'])
def sliceModel():
    modelName = request.args.get('modelName')
    shell = '~/cura/CuraEngine2.5 slice -v -p -j ~/cura/resources/definitions/delta.def.json' \
            ' -o ~/cura/output/' + modelName + '.gcode -l ~/cura/models/' + modelName + '.stl'
    result = os.popen(shell).read()
    return result
