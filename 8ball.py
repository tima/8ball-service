#!/usr/bin/env python

import random
import socket
from flask import Flask, request, jsonify, render_template

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

host_ip4 = socket.gethostbyname(socket.gethostname())

@app.route('/', methods=['GET'])
def shake_8ball():
    res = {
        'answer': answers[random.randint(0, len(answers))-1],
        'host_ip4': host_ip4,
    }
    if request.accept_mimetypes['text/html'] > request.accept_mimetypes['application/json']:
        return render_template('8ball.j2', res=res)
        # return '<html><body><h1>' + res['answer'] + '</h1></body></html>'
    return jsonify(res)

if __name__ == "__main__":
    app.run(debug=True)

