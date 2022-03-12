from datetime import timedelta
import os

bazaKontejner = os.environ["BAZA_AUTH_KONTEJNER"]


class Configuration():
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@{bazaKontejner}/autorizacija"
    JWT_SECRET_KEY = "JWT_SECRET_KEY"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=60)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

