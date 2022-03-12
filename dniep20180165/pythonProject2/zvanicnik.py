import csv
import io

import flask
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, get_jwt
from redis import Redis

from bazaglasanje import databaseGlasanje
from configuration2 import Configuration2
from dekorater import roleCheck

application = Flask(__name__)


def represents_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


jwt = JWTManager(application)


@application.route("/vote", methods=["POST"])
@roleCheck(role="zvanicnik")
def glasaj():
    # if 'file' not in request.files:
    #     return jsonify(message="Field file missing.")
    # file = request.files['file']
    #
    # with open(file, mode='r') as csv_file:
    #     csv_reader = csv.DictReader(csv_file)
    #     i = -1
    #     for row in csv_reader:
    #         red = ",".join(row)
    #         i += 1
    #         if len(red) != 2:
    #             return jsonify(message="Incorrect number of values on line {}.".format(i))
    #         if not represents_int(red[1]) or not int(red[1]) > 0:
    #             return jsonify(message="Incorrect poll number on line {}.".format(i))
    #         with Redis(host=Configuration2.REDIS_HOST) as redis:
    #             redis.rpush(Configuration2.REDIS_THREADS_LIST, row)
    #             redis.lrange(Configuration2.REDIS_THREADS_LIST , 0 , -1)

    content = request.files.get("file", "")
    if content == "":
        return jsonify(message="Field file is missing."), 400
    content = content.stream.read().decode("utf-8");
    stream = io.StringIO(content)
    reader = csv.reader(stream)
    claims = get_jwt();
    jmbg = claims["jmbg"]
    comments = []
    i = -1
    for row in reader:
        i += 1
        if len(row) != 2:
            return jsonify(message="Incorrect number of values on line {}.".format(i)), 400
        if not represents_int(row[1]) or not int(row[1]) > 0:
            return jsonify(message="Incorrect poll number on line {}.".format(i)), 400
        comments.append(row[0] + "@" + row[1] + "@" + jmbg)

    with Redis(host=Configuration2.REDIS_HOST, decode_responses=True) as redis:
        for c in comments:
            redis.rpush(Configuration2.REDIS_THREADS_LIST, c)
    #redis.flushall(False)

    status_code = flask.Response(status=200)
    return status_code


application.config.from_object(Configuration2)

if __name__ == "__main__":
    databaseGlasanje.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=6002)
