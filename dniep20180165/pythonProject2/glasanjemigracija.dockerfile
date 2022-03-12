FROM python:3

RUN mkdir -p /opt/src/authentication
WORKDIR /opt/src/authentication

COPY admin.py ./admin.py
COPY bazaglasanje.py ./bazaglasanje.py
COPY glasanjemigracija.py ./glasanjemigracija.py
COPY configuration2.py ./configuration2.py
COPY dekorater.py ./dekorater.py
COPY demon.py ./demon.py
COPY requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

ENV DATABASE_URL="/opt/src"


ENTRYPOINT ["python", "./glasanjemigracija.py"]
