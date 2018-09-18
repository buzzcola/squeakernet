'''
A friendly web interface with information from the feeder and the ability to trigger a feed.
'''

from bottle import route, run, template, static_file, post, request
import psutil
import ConfigParser
import os
import sys
import re
import datetime
import json
import squeakernet_db
from squeakernet_db import LogCategory
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
    client_ip = request.environ.get('REMOTE_ADDR')
    local_pattern = '(^192\.168\.([0-9]|[0-9][0-9]|[0-2][0-5][0-5])\.([0-9]|[0-9][0-9]|[0-2][0-5][0-5])$)|(^172\.([1][6-9]|[2][0-9]|[3][0-1])\.([0-9]|[0-9][0-9]|[0-2][0-5][0-5])\.([0-9]|[0-9][0-9]|[0-2][0-5][0-5])$)|(^10\.([0-9]|[0-9][0-9]|[0-2][0-5][0-5])\.([0-9]|[0-9][0-9]|[0-2][0-5][0-5])\.([0-9]|[0-9][0-9]|[0-2][0-5][0-5])$)'
    if len(re.findall(local_pattern, client_ip)) > 0:
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
    return squeakernet_db.get_last_log(LogCategory.WEIGHT).to_json()

@route('/api/lastFeed')
def last_feed():
    return squeakernet_db.get_last_log(LogCategory.FEED).to_json()

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