from datetime import datetime, timedelta

import pytz
from dateutil import parser
from flask import Flask
from flask_jwt_extended import JWTManager
from redis import Redis

from bazaglasanje import databaseGlasanje, Izbori, Glas
from configuration2 import Configuration2

application = Flask(__name__)
application.config.from_object(Configuration2)
jwt = JWTManager(application)


@application.route("/", methods=["GET"])
def index():
    return "Hello dameon!"


def main(vote):
    print(vote)
    podaci_o_glasu = vote.split("@")
    utc = pytz.UTC

    izbori = Izbori.query.all()
    trenutno = parser.isoparse(datetime.now().isoformat())
    hours_to_add = timedelta(hours=2)
    trenutno = trenutno + hours_to_add
    trenutno = trenutno + timedelta(seconds=1)
    trenutno = trenutno + timedelta(milliseconds=70)
    #trenutno = trenutno + timedelta(seconds=2)
    trenutno_izbori = False
    izboriid = -1

    for izbor in izbori:
        pocetak = parser.isoparse(izbor.start)
        kraj = parser.isoparse(izbor.end)
        if pocetak < trenutno < kraj:
            trenutno_izbori = True
            izboriid = izbor.id
            break

    if not trenutno_izbori:
        print("No elections")
        return

    votee = Glas.query.filter(Glas.guid == podaci_o_glasu[0]).first()

    if votee:
        novi = Glas(guid=podaci_o_glasu[0], jmbg=podaci_o_glasu[2], izboriid=izboriid, kandidat=int(podaci_o_glasu[1]),
                    validan=False,
                    razlog="Duplicate ballot.")

        databaseGlasanje.session.add(novi)
        databaseGlasanje.session.commit()

    else:
        broj_ucesnika_na_izborima = 0
        izborii = Izbori.query.filter(Izbori.id == izboriid).first()

        for ucesnik in izborii.ucesnik:
            broj_ucesnika_na_izborima += 1

        candidate = int(podaci_o_glasu[1])
        if candidate > broj_ucesnika_na_izborima:
            novi = Glas(guid=podaci_o_glasu[0], jmbg=podaci_o_glasu[2], izboriid=izboriid, kandidat=candidate,
                        validan=False,
                        razlog="Invalid poll number.")

            databaseGlasanje.session.add(novi)
            databaseGlasanje.session.commit()

        else:
            novi = Glas(guid=podaci_o_glasu[0], jmbg=podaci_o_glasu[2], izboriid=izboriid, kandidat=candidate, validan=True)

            databaseGlasanje.session.add(novi)
            databaseGlasanje.session.commit()


if __name__ == "__main__":
    databaseGlasanje.init_app(application)

    with application.app_context():
        while True:
            with Redis(host=Configuration2.REDIS_HOST) as redis:
                _, message = redis.blpop(Configuration2.REDIS_THREADS_LIST)
                message = message.decode("utf-8")
                print(message)
                main(message)
