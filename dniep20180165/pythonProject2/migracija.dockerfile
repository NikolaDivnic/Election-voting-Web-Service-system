FROM python:3

RUN mkdir -p /opt/src/authentication
WORKDIR /opt/src/authentication

COPY autorizacija.py ./autorizacija.py
COPY configuration.py ./configuration.py
COPY dekorater.py ./dekorater.py
COPY migrate.py ./migrate.py
COPY models.py ./models.py
COPY requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

ENV DATABASE_URL="/opt/src"


ENTRYPOINT ["python", "./migrate.py"]
