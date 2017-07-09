# -*- coding: utf-8 -*-
import os
import subprocess
import urllib

from flask import jsonify, make_response, request, send_from_directory, send_file
from . import main


@main.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not Found'}), 404)


@main.route('/<string:name>', methods=['GET', 'POST'])
def index(name):
    if name == '':
        return '万创科技'
    else:
        outName = name.split('.', 1)[0]
        shell = '~/cura/CuraEngine2.5 slice -v -j ~/cura/resources/definitions/delta.def.json' \
                ' -o ~/cura/output/' + outName + '.gcode -l ~/cura/models/' + name
        os.popen(shell).read()
        return send_file('../../../cura/output/' + outName + '.gcode', as_attachment=True)


# ~/cura/CuraEngine2.5 slice -v -p -j ~/cura/resources/definitions/delta.def.json -o ~/cura/output/1.gcode -l ~/cura/models/1.stl


@main.route('/download', methods=['POST'])
def download():
    filePath = '../../../cura/input/' + request.json['name']
    fileUrl = request.json['url']
    urllib.urlretrieve(fileUrl, filePath)
