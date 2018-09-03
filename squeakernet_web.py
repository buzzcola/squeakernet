'''
A friendly web interface with information from the feeder and (soon) the ability to trigger a feeding.
'''

from bottle import route, run, template, static_file, post
import psutil
import ConfigParser
import os
import sys
import datetime
import json
import squeakernet_db
import squeakernet

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

@post('/feed')
def feed():
    squeakernet.feed_the_cats()

@route('/cpu')
def cpu():
    return str(psutil.cpu_percent())

@route('/temp')
def temp():
    command_result = os.popen('vcgencmd measure_temp').readline()
    result = command_result.replace("temp=","").replace("'C\n","")
    # will fail (500) on an OS that doesn't have this command (that's ok.)
    return str(float(result))

@route('/weight')
def weight():
    # placholder until I get the HX711 working.
    return str(50)

@route('/lastFeed')
def last_feed():
    return str(squeakernet_db.get_last_feed())

run(host='0.0.0.0', port=port)