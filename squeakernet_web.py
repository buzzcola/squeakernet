'''
A friendly web interface with information from the feeder and the ability to trigger a feed.
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

# Content Pages
@route('/')
def index():
    return serve_file('index.html')

@route('/logs')
def logs_page():
    return serve_file('logs.html')

# serve all file contents in the folder and subfolders.
@route('/<filepath:path>')
def serve_file(filepath):
    return static_file(filepath, root)

# API routes
@post('/api/feed')
def feed():
    squeakernet.feed_the_cats()

@route('/api/cpu')
def cpu():
    return str(psutil.cpu_percent())

@route('/api/temp')
def temp():
    command_result = os.popen('vcgencmd measure_temp').readline()
    result = command_result.replace("temp=","").replace("'C\n","")
    # will fail (500) on an OS that doesn't have this command (that's ok.)
    return str(float(result))

@route('/api/weight')
def weight():
    # placholder until I get the HX711 working.
    return str(50)

@route('/api/lastFeed')
def last_feed():
    return str(squeakernet_db.get_last_feed())

@route('/api/logs')
def logs():
    logs = squeakernet_db.get_logs()
    log_dict = [{'id': x[0],
                'date': x[1],
                'category': x[2],
                'message': x[3],
                'reading': x[4]} for x in logs]
    return json.dumps(log_dict)

if __name__ == '__main__':
    squeakernet_db.write_log(squeakernet_db.LogCategory.SYSTEM, 'squeakernet_web started on port %d.' % port)
    run(host='0.0.0.0', port=port)