import random
import socket
import time
from functools import wraps

from flask import Flask, Response, g, request, jsonify, render_template

app = Flask(__name__)

answers = [
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

hostname = socket.getfqdn()

try:
    from statsd import StatsClient
    HAS_STATSD = True
except ImportError:
    HAS_STATSD = False

# temporary config
stats_enabled = True
stats_ms_rounding =  False 
# node_name = node-1

def stats_collected(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if stats_enabled:
            start = time.time()
            rv = f(*args, **kwargs)
            end = time.time()
            delta = (end-start) * 1000 
            if stats_ms_rounding:
                delta = int(delta)
            if not hasattr(g, 'statsd'):
                g.statsd = StatsClient(prefix='8ball') 
            (x, mimetype) = rv.mimetype.split('/')
            g.statsd.incr(mimetype)
            g.statsd.timing(mimetype, delta)
        else:
           rv = f(*args, **kwargs)
        return rv
    return wrapper 

@stats_collected
def shake_8ball(force_json=False):
    res = {
        'answer': answers[random.randint(0, len(answers))-1],
        'hostname': hostname
    }
    # time.sleep(random.uniform(0,0.2))
    if not force_json and request.accept_mimetypes['text/html'] > request.accept_mimetypes['application/json']:
        return Response(response=render_template('8ball.j2', res=res), status=200, mimetype='text/html')
    return jsonify(res)

@app.route('/', methods=['GET'])
def default_handler():
    return shake_8ball()

@app.route('/json', methods=['GET'])
def force_json_handler():
    return shake_8ball(force_json=True)

if __name__ == "__main__":
    app.run(host='0.0.0.0')

