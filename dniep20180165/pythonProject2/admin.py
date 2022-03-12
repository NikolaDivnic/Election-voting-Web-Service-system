import flask
import json

import pytz
from flask import Flask, request, jsonify, make_response
from flask_jwt_extended import JWTManager
from datetime import timedelta

from configuration2 import Configuration2
from dekorater import roleCheck
from datetime import datetime
from dateutil import parser

from bazaglasanje import databaseGlasanje, Ucesnik, Izbori, Prijavljennaizborima,Glas

application = Flask(__name__)


def greska_prilikom_zahteva_za_kreiranje_ucesnika(name, individual):
    greska = ''
    if name == '':
        greska = "Field name is missing."

    if greska != '':
        return greska
    if individual == '':
        greska = "Field individual is missing."

    if greska != '':
        return greska
    return ''


def napravi_ucesnika(name, individual):
    tag = Ucesnik(name=name, individual=individual)
    databaseGlasanje.session.add(tag)
    databaseGlasanje.session.commit()
    return tag.id





def datetime_valid(dt_str):
    try:
        parser.isoparse(dt_str)
    except:
        return False
    return True


def nije_sve_uneto_prilikom_kreiranja_izbora(start, end, individual, participants):
    greska = ''
    if start == '':
        greska = "Field start is missing."
    if greska != '':
        return greska
    if end == '':
        greska = "Field end is missing."
    if greska != '':
        return greska
    if individual == '':
        greska = "Field individual is missing."
    if greska != '':
        return greska
    if participants == '':
        greska = "Field participants is missing."
    if greska != '':
        return greska

    return ''


def nisu_svi_ucesnici_prijavljani_na_odgovarajuce_izbore(individual, participants):
    ucesnici = Ucesnik.query.all()
    try:
        int(participants[1])
        for k in ucesnici:
            for p in participants:
                if k.id == p:
                    if individual != k.individual:
                        return True
    except TypeError:
        return True
    return False


def greska_prilikom_zahteva_za_kreiranje_izbora(start, end, individual, participants):

    greska = nije_sve_uneto_prilikom_kreiranja_izbora(start, end, individual, participants)
    if greska != '':
        return greska
    # trenutno = parser.isoparse(datetime.now().isoformat())
    # hours_to_add = timedelta(hours=2)
    # trenutno = trenutno + hours_to_add

    if not (datetime_valid(start) and datetime_valid(end) and end >start):
        return "Invalid date and time."
    utc = pytz.UTC
    elections = Izbori.query.all()
    startDate = parser.isoparse(start)
    endDate = parser.isoparse(end)

    startDate = startDate.replace(tzinfo=utc)
    endDate = endDate.replace(tzinfo=utc)

    for election in elections:
        electionStart = parser.isoparse(election.start)
        electionEnd = parser.isoparse(election.end)

        electionStart = electionStart.replace(tzinfo=utc)
        electionEnd = electionEnd.replace(tzinfo=utc)

        if ((startDate > electionStart and startDate < electionEnd) or (
                endDate > electionStart and endDate < electionEnd)):
            return "Invalid date and time."


    if len(participants) < 2:
        return "Invalid participants."
    if nisu_svi_ucesnici_prijavljani_na_odgovarajuce_izbore(individual, participants):
        return "Invalid participants."

    return ''


def dodaj_izbore(start, end, individual):
    tag = Izbori(start=start, end=end, individual=individual)
    databaseGlasanje.session.add(tag)
    databaseGlasanje.session.commit()
    return tag.id


def dodaj_ucesnika_na_izborima(idizbora, p):
    tag = Prijavljennaizborima(ucesnikID=p, izboriID=idizbora)
    databaseGlasanje.session.add(tag)
    databaseGlasanje.session.commit()


def napravi_izbore(start, end, individual, participants):
    idizbora = dodaj_izbore(start, end, individual)
    niz = []
    i = 0
    for p in participants:
        i += 1
        dodaj_ucesnika_na_izborima(idizbora, p)
        niz.append(i)
    return niz


def nadji_ucesnike_na_izborima(id):
    prijavljani_na_izborima = Prijavljennaizborima.query.filter_by(izboriID=id).all()

    niz = []
    for u in prijavljani_na_izborima:
        ucesnik = Ucesnik.query.filter_by(id=u.ucesnikID).first()
        niz.append({
            "id": u.id,
            "name": ucesnik.name
        })


def napravi_json_objekat(greska):
    data = {
        "message": greska
    }
    json_data = json.dumps(data)
    return json_data


jwt = JWTManager(application)


def nepostoje_izbori_sa_tim_idom(id):
    if Izbori.query.filter(Izbori.id == id).first():
        return False
    return True


def izbori_jos_uvek_traju(id):
    izbori = Izbori.query.all()
    trenutno = parser.isoparse(datetime.now().isoformat())
    hours_to_add = timedelta(hours=2)
    trenutno = trenutno + hours_to_add

    for izbor in izbori:
        pocetak = parser.isoparse(izbor.start)
        kraj = parser.isoparse(izbor.end)
        if pocetak < trenutno < kraj:
            return True
    return False


def greska_prilikom_zahteva_za_dohvatanje_rezultata_izbora(id):
    if id == "":
        return "Field id is missing."
    if nepostoje_izbori_sa_tim_idom(id):
        return "Election does not exist."
    if izbori_jos_uvek_traju(id):
        return "Election is ongoing."
    return ""


def racunaj_broj_mandata(broj_glasova, dobili_glasove):
    niz_mandata = []
    for i in range(len(dobili_glasove)):
        niz_mandata.append(1)
        if dobili_glasove[i] * 20 < broj_glasova:
            dobili_glasove[i] = 0
    m = 0
    trenutni = 0
    for i in range(250):
        for j in range(len(dobili_glasove)):
            if m < (float(dobili_glasove[j]) / float(niz_mandata[j])):
                m = float(dobili_glasove[j]) / float(niz_mandata[j])
                trenutni = j
        niz_mandata[trenutni] += 1
        m = 0

    for i in range(len(dobili_glasove)):
        niz_mandata[i] -= 1

    return niz_mandata


def racunaj_rezultat_na_predsednickim(broj_glasova, dobili_glasove):
    niz = []
    for i in range(len(dobili_glasove)):
        if int(dobili_glasove[i]) == 0:
            niz.append(0)
        else:
            niz.append(int(dobili_glasove[i]) / int(broj_glasova))
    return niz

def dohvati_rezultate_izbore(izbori, predsednicki):
    ucesnici = izbori.ucesnik
    glasovi = izbori.glasovi
    broj_glasova = 0
    nevazeci_glasovi = []
    for g in glasovi:
        if g.validan:
            broj_glasova += 1
        else:
            nevazeci_glasovi.append(g)

    dobili_glasove = []
    for i in range(len(ucesnici)):
        dobili_glasove.append(0)
    for g in glasovi:
        if g.validan :
            dobili_glasove[g.kandidat - 1] += 1

    broj_mandata = []
    if predsednicki:
        broj_mandata = racunaj_rezultat_na_predsednickim(broj_glasova, dobili_glasove)
    else:
        broj_mandata = racunaj_broj_mandata(broj_glasova, dobili_glasove)

    i = 0
    nizucesnika = []
    if predsednicki:
        for u in ucesnici:
            pom = {
                "pollNumber": i + 1,
                "name": u.name,
                "result": float("{:.2f}".format(broj_mandata[i]))
            }
            i += 1
            nizucesnika.append(pom)
    else:
        for u in ucesnici:
            pom = {
                "pollNumber": i + 1,
                "name": u.name,
                "result": broj_mandata[i]
            }
            i += 1
            nizucesnika.append(pom)
    nevazeci = []
    for n in nevazeci_glasovi:
        pom = {
            "electionOfficialJmbg": n.jmbg,
            "ballotGuid": n.guid,
            "pollNumber": n.kandidat,
            "reason": n.razlog
        }
        nevazeci.append(pom)
    return jsonify(participants=nizucesnika, invalidVotes=nevazeci)


def dohvati_izbore(id):
    izbori = Izbori.query.filter(Izbori.id == id).first()
    return dohvati_rezultate_izbore(izbori, izbori.individual)


@application.route("/getResults", methods=["GET"])
@roleCheck(role="admin")
def dohvatirezultatizbora():
    id_izbora = request.args.get("id", "")
    if (len(str(id_izbora)) == 0):
        return jsonify(message="Field id is missing."), 400
    if id_izbora == "":
        return flask.Response(napravi_json_objekat("Field id is missing."), status=400)
    #election = Izbori.query.filter(Izbori.id == id).first()

    #if (not election):
     #   return flask.Response(napravi_json_objekat("Election does not exist."), status=401)
    if len(Izbori.query.filter(Izbori.id == id_izbora).all()) == 0:
        return flask.Response(napravi_json_objekat("Election does not exist."), status=400)
    if izbori_jos_uvek_traju(id_izbora):
        return flask.Response(napravi_json_objekat("Election is ongoing."), status=400)
    #greska = greska_prilikom_zahteva_za_dohvatanje_rezultata_izbora(id_izbora)
    #if greska != '':
     #   return flask.Response(napravi_json_objekat(greska), status=400)

    return dohvati_izbore(id_izbora)


@application.route("/getElections", methods=["GET"])
@roleCheck(role="admin")
def dohvatiizbore():
    izbori = Izbori.query.all()
    niz = []
    nizucesnika = []
    for k in izbori:
        ucesnici = k.ucesnik

        for u in ucesnici:
            pom = {
                "id": u.id,
                "name": u.name,
            }
            nizucesnika.append(pom)

        pom = {
            "id": k.id,
            "start": k.start,
            "end": k.end,
            "individual": k.individual,
            "participants": nizucesnika
        }
        nizucesnika = []
        niz.append(pom)
    return jsonify(elections=niz)


@application.route("/createElection", methods=["POST"])
@roleCheck(role="admin")
def napraviizbore():
    start = request.json.get("start", "")
    end = request.json.get("end", "")
    individual = request.json.get("individual", "")
    participants = request.json.get("participants", "")

    greska = greska_prilikom_zahteva_za_kreiranje_izbora(start, end, individual, participants)
    if greska != '':
        return flask.Response(napravi_json_objekat(greska), status=400)

    niz = napravi_izbore(start, end, individual, participants)
    return jsonify(pollNumbers=niz)


@application.route("/getParticipants", methods=["GET"])
@roleCheck(role="admin")
def dohvatiucesnike():
    ucesnici = Ucesnik.query.all()
    niz = []
    for k in ucesnici:
        pom = {
            "id": k.id,
            "name": k.name,
            "individual": k.individual
        }
        niz.append(pom)
    return jsonify(participants=niz)


@application.route("/createParticipant", methods=["POST"])
@roleCheck(role="admin")
def creirajucesnika():
    name = request.json.get("name", "")
    individual = request.json.get("individual", "")
    greska = greska_prilikom_zahteva_za_kreiranje_ucesnika(name, individual)
    if greska != '':
        return flask.Response(napravi_json_objekat(greska), status=400)
    # return jsonify(id="pera")
    id_ucesnika = napravi_ucesnika(name, individual)
    return jsonify(id=id_ucesnika)



@application.route("/nadji/<rec>", methods=["GET"])
def nadji(rec = None):

    glasovi = Glas.query.all()
    niz =[]
    for g in glasovi:
        if g.guid.find(rec)!=-1:
            niz.append(g.guid)

    return jsonify(glasovi = niz)

@application.route("/nadjiizbore/<idu>", methods=["GET"])
def nadjiiz(idu = None):
    #return jsonify(glasovi = idu)
    izb = Prijavljennaizborima.query.filter(Prijavljennaizborima.ucesnikID == idu).all()
    svi = Izbori.query.all()
    izbori  = []
    for i in izb:
        for s in svi:
            if i.izboriID == s.id:
                izbori.append(s)
    trenutno = parser.isoparse(datetime.now().isoformat())
    hours_to_add = timedelta(hours=2)
    trenutno = trenutno + hours_to_add
    #return jsonify(glasovi=trenutno)
    niz =[]
    for izbor in izbori:
        pocetak = parser.isoparse(izbor.start)
        kraj = parser.isoparse(izbor.end)
        if pocetak < trenutno < kraj:
            niz.append(izbor.id)

    return jsonify(glasovi = niz)
application.config.from_object(Configuration2)

if __name__ == "__main__":
    databaseGlasanje.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=6001)
