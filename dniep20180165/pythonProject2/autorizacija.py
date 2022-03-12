import flask
import json
import re
from flask import Flask, request, jsonify, make_response
from configuration import Configuration
from dekorater import roleCheck
from models import database, User
from flask_jwt_extended import JWTManager, create_access_token, \
    jwt_required, create_refresh_token, get_jwt, get_jwt_identity
from sqlalchemy import and_

application = Flask(__name__)


def odredi_broj_dana_za_februar(year):
    if year < 100:
        year += 1000
    year += 1000
    if (year % 4) == 0:
        if (year % 100) == 0:
            if (year % 400) == 0:
                return 29
            else:
                return 28
        else:
            return 29
    else:
        return 28


def odredi_broj_dana_po_mesecima(godina):
    return {
        1: 31,
        2: odredi_broj_dana_za_februar(godina),
        3: 31,
        4: 30,
        5: 31,
        6: 30,
        7: 31,
        8: 31,
        9: 30,
        10: 31,
        11: 30,
        12: 31
    }


def neispravan_dan(dan, mesec, godina):
    meseci = odredi_broj_dana_po_mesecima(godina)
    return dan > meseci[mesec] or dan < 1


def neispravan_mesec(mesec):
    return mesec < 1 or mesec > 12


def neispravan_region(region):
    return region < 70 or region > 99


def neispravna_kontrolna_cifra(jmbg, kontrolnacifra):
    m = 11 - ((7 * (int(jmbg[0]) + int(jmbg[6])) + 6 * (int(jmbg[1]) + int(jmbg[7])) + 5 * (int(jmbg[2])
                                                                                            + int(jmbg[8])) + 4 * (
                       int(jmbg[3]) + int(jmbg[9])) + 3 * (int(jmbg[4]) + int(jmbg[10]))
               + 2 * (int(jmbg[5]) + int(jmbg[11]))) % 11)

    if m > 9:
        if kontrolnacifra == 0:
            return False
        return True
    if kontrolnacifra == m:
        return False
    return True


def provera_neispravan_jmbg(jmbg, dan, mesec, godina, region, kontrolnacifra):
    return neispravan_mesec(mesec) or neispravan_dan(dan, mesec, godina) or neispravan_region(region) \
           or neispravna_kontrolna_cifra(jmbg, kontrolnacifra)


def represents_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def neispravan_jmbg(jmbg):
    if len(jmbg) != 13 or not represents_int(jmbg):
        return True

    dan = int(jmbg[0:2])
    mesec = int(jmbg[2:4])
    godina = int(jmbg[4:7])
    region = int(jmbg[7:9])
    kontrolnacifra = int(jmbg[12:13])
    return provera_neispravan_jmbg(jmbg, dan, mesec, godina, region, kontrolnacifra)


def nije_sve_uneto(jmbg, forename, surname, email, password):
    if jmbg == '':
        return " jmbg"
    if forename == '':
        return " forename"
    if surname == '':
        return " surname"
    if email == '':
        return " email"
    if password == '':
        return " password"
    return ''


def neispravno_ime(forename):
    return len(forename) > 256


def neispravno_prezime(surname):
    return len(surname) > 256


def nije_mejl(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if re.match(regex, email):
        return False
    else:
        return True


def neispravan_email(email):
    return len(email) > 256 or nije_mejl(email)


def has_numbers(inputstring):
    return any(char.isdigit() for char in inputstring)


def ima_malih_slova(password):
    for c in password:
        if c.islower():
            return True
    return False


def ima_velikih_slova(password):
    for c in password:
        if c.isupper():
            return True
    return False


def neispravna_sifra(password):
    return len(password) > 256 or len(password) < 8 or not has_numbers(password) \
           or not ima_malih_slova(password) or not ima_velikih_slova(password)


def postoji_vec_email(email):
    niz = User.query.all()
    for k in niz:
        if k.email == email:
            return True
    return False


def sve_uneto_ali_neispravno(jmbg, forename, surname, email, password):
    greska = ''
    imagreske = False
    if neispravan_jmbg(jmbg):
        imagreske = True
        greska = "Invalid jmbg."
    if neispravno_ime(forename) and not imagreske:
        imagreske = True
        greska = "Invalid forename."
    if neispravno_prezime(surname) and not imagreske:
        imagreske = True
        greska = "Invalid surname."
    if neispravan_email(email) and not imagreske:
        imagreske = True
        greska = "Invalid email."
    if neispravna_sifra(password) and not imagreske:
        imagreske = True
        greska = "Invalid password."
    if postoji_vec_email(email) and not imagreske:
        greska = "Email already exists."
    return greska


def provera_zahteva(jmbg, forename, surname, email, password):
    fali = nije_sve_uneto(jmbg, forename, surname, email, password)

    if fali != '':
        return "Field" + fali + " is missing."

    return sve_uneto_ali_neispravno(jmbg, forename, surname, email, password)


def napravi_json_objekat(greska):
    data = {
        "message": greska
    }
    json_data = json.dumps(data)
    return json_data


def povratna_poruka(greska):
    if greska != '':
        return flask.Response(napravi_json_objekat(greska), status=400)

    status_code = flask.Response(status=200)
    return status_code


def napravi_korisnika(jmbg, forename, surname, email, password):
    tag = User(jmbg=jmbg, forename=forename, surname=surname, email=email, password=password, role="zvanicnik")
    database.session.add(tag)
    database.session.commit()


def provera_da_li_su_podaci_uneti(email, password):
    fali = ""
    if email == '':
        return "Field email is missing."
    if password == '':
        return "Field password is missing."

    return fali


def nije_dobra_sifra(email, password):
    niz = User.query.all()
    for k in niz:
        if k.email == email and k.password == password:
            return False
    return True


def ne_postoji_korisnik(email):
    niz = User.query.all()
    for k in niz:
        if k.email == email:
            return False
    return True


def greska_prilikom_zahteva_za_prijavu(email, password):
    greska = provera_da_li_su_podaci_uneti(email, password)
    if greska != '':
        return greska
    greska = neispravan_email(email)
    if greska:
        return "Invalid email."
    greska = ne_postoji_korisnik(email)
    if greska:
        return "Invalid credentials."
    greska = nije_dobra_sifra(email, password)
    if greska:
        return "Invalid password."

    return ''





def obrisi_korisnika(email):
    User.query.filter_by(email=email).delete()
    database.session.commit()


@application.route("/delete", methods=["POST"])
@roleCheck(role="admin")
def obrisi():

    email = request.json.get("email", "")

    greska = ''
    if email == '':
        return make_response(jsonify(message="Field email is missing."), 400)

    if greska != '':
        return greska
    greska = neispravan_email(email)
    if greska:
        return make_response(jsonify(message="Invalid email."), 400)

    niz = User.query.all()
    fleg = True
    for k in niz:
        if k.email == email:
            fleg = False

    if fleg:
        return make_response(jsonify(message="Unknown user."), 400)

    obrisi_korisnika(email)
    status_code = flask.Response(status=200)
    return status_code


@application.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    refresh_claims = get_jwt()

    additional_claims = {
        "forename": refresh_claims["forename"],
        "surname": refresh_claims["surname"],
        "role": refresh_claims["role"],
        "jmbg": refresh_claims["jmbg"]
    }

    access_token = create_access_token(identity=identity, additional_claims=additional_claims)
    return jsonify(accessToken=access_token)


jwt = JWTManager(application)


@application.route("/login", methods=["POST"])
def login():
    email = request.json.get("email", "")
    password = request.json.get("password", "")
    greska = greska_prilikom_zahteva_za_prijavu(email, password)
    if greska != '':
        return flask.Response(napravi_json_objekat(greska), status=400)
    korisnik = User.query.filter(and_(User.email == email, User.password == password)).first()
    if not korisnik:
        return make_response(jsonify(message="Invalid credentials."), 400);

    additional_claims = {
        "forename": korisnik.forename,
        "surname": korisnik.surname,
        "role": korisnik.role,
        "jmbg": korisnik.jmbg
    }

    access_token = create_access_token(identity=korisnik.email, additional_claims=additional_claims)
    refresh_token = create_refresh_token(identity=korisnik.email, additional_claims=additional_claims)
    return jsonify(accessToken=access_token, refreshToken=refresh_token)


@application.route("/register", methods=["POST"])
def index():
    jmbg = request.json.get("jmbg", "")
    forename = request.json.get("forename", "")
    surname = request.json.get("surname", "")
    email = request.json.get("email", "")
    password = request.json.get("password", "")
    greska = provera_zahteva(jmbg, forename, surname, email, password)
    if greska == '':
        napravi_korisnika(jmbg, forename, surname, email, password)
    return povratna_poruka(greska)


application.config.from_object(Configuration)

if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=6000)
