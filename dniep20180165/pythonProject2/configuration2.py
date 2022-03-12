from datetime import timedelta
import os

bazaKontejner = os.environ["BAZA_AUTH_KONTEJNER"]
r = os.environ["REDIS"]

class Configuration2():
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@{bazaKontejner}/admin"
    JWT_SECRET_KEY = "JWT_SECRET_KEY"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=60)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    REDIS_HOST = r
    REDIS_THREADS_LIST = "glasovi"
