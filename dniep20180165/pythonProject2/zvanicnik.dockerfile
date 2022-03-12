FROM python:3

RUN mkdir -p /opt/src/authentication
WORKDIR /opt/src/authentication

COPY bazaglasanje.py ./bazaglasanje.py
COPY glasanjemigracija.py ./glasanjemigracija.py
COPY dekorater.py ./dekorater.py
COPY demon.py ./demon.py
COPY configuration2.py ./configuration2.py
COPY requirements.txt ./requirements.txt
COPY zvanicnik.py ./zvanicnik.py

RUN pip install -r ./requirements.txt

ENV DATABASE_URL="/opt/src"


ENTRYPOINT ["python", "./zvanicnik.py"]
