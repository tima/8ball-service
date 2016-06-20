#!/usr/bin/env python

import random
import socket
from flask import Flask, jsonify

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

hostname_ip4 = socket.gethostbyname(socket.gethostname())

@app.route('/', methods=['GET'])
def shake_8ball():
    answer = answers[random.randint(0, len(answers))-1]
    return jsonify({'answer': answer, 'hostname_ip4': hostname_ip4})

if __name__ == "__main__":
    app.run(debug=True)

