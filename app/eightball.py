import os
import sys
import random
import socket
import time
from functools import wraps

from flask import Flask, Response, g, request, jsonify, render_template

eightball_answers = [
        "It is certain",
        "It is decidedly so",
        "Without a doubt",
        "Yes definitely",
        "You may rely on it",
        "As I see it yes",
        "Most likely",
        "Outlook good",
        "Yes",
        "Signs point to yes",
        "Reply hazy try again",
        "Ask again later",
        "Better not tell you now",
        "Cannot predict now",
        "Concentrate and ask again",
        "Don't count on it",
        "My reply is no",
        "My sources say no",
        "Outlook not so good",
        "Very doubtful",
]

def str2bool(v):
    return v.lower() in ['true', '1', 'yes']

# init app with config
app = Flask(__name__)
stats_enabled = str2bool(os.getenv('EIGHTBALL_STATS_ENABLED', 'no'))
nodename = os.getenv('EIGHTBALL_NODENAME', socket.gethostname())
influxdb_host = os.getenv('EIGHTBALL_INFLUXDB_HOST', 'localhost')

try:
    from influxdb import InfluxDBClient
    HAS_INFLUXDB = True
except ImportError, err:
    HAS_INFLUXDB = False

if stats_enabled and not HAS_INFLUXDB:
    sys.stderr.write('ERROR: %s' % str(err))
    sys.exit(1)


def stats_collected(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if stats_enabled:
            start = time.time()
            rv = f(*args, **kwargs)
            end = time.time()
            delta = (end-start) * 1000 
            (x, mimetype) = rv.mimetype.split('/')
            if not hasattr(g, 'influxdb'):
                g.influxdb = InfluxDBClient(host=influxdb_host, database='8ball')
            try:
                g.influxdb.create_database('8ball')
            except:
                pass
            stats_body = [
                {
                    'measurement': '8ball',
                    'tags': { 'mimetype': mimetype },
                    'fields': { 'response': 1 } 
                },
                {
                    'measurement': '8ball',
                    'tags': { 'mimetype': mimetype },
                    'fields': { 'response_time': delta }
                }
            ]
            g.influxdb.write_points(stats_body)
        else:
           rv = f(*args, **kwargs)
        return rv
    return wrapper 

@stats_collected
def shake_8ball(force_json=False):
    res = {
        'answer': eightball_answers[random.randint(0, len(eightball_answers))-1],
        'nodename': nodename
    }
    # time.sleep(random.uniform(0,0.2))
    if not force_json and request.accept_mimetypes['text/html'] > request.accept_mimetypes['application/json']:
        return Response(response=render_template('8ball.j2', eightball=res), status=200, mimetype='text/html')
    return jsonify(res)

@app.route('/', methods=['GET'])
def default_handler():
    return shake_8ball()

@app.route('/json', methods=['GET'])
def force_json_handler():
    return shake_8ball(force_json=True)

if __name__ == "__main__":
    app.run(host='0.0.0.0')

