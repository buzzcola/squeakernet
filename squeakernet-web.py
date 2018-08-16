from bottle import route, run, template, static_file
import ConfigParser
import os
import sys

config = ConfigParser.ConfigParser()
config.read(os.path.join(sys.path[0], "squeakernet.ini"))
port = config.getint('web', 'port')
host = config.get('web', 'host')
root = os.path.join(sys.path[0], 'site')

@route('/')
def index():
    return serve_file('index.html')

@route('/<filepath:path>')
def serve_file(filepath):
    return static_file(filepath, root)

run(host='0.0.0.0', port=port)