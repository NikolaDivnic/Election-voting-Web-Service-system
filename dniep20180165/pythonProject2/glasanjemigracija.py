from flask import Flask
from flask_migrate import Migrate, init, migrate, upgrade
from sqlalchemy_utils import database_exists, create_database

from bazaglasanje import databaseGlasanje
from configuration2 import Configuration2

application = Flask(__name__)
application.config.from_object(Configuration2)

migrateObject = Migrate(application, databaseGlasanje)

if not database_exists(application.config["SQLALCHEMY_DATABASE_URI"]):
    create_database(application.config["SQLALCHEMY_DATABASE_URI"])

databaseGlasanje.init_app(application)

with application.app_context() as context:
    init()
    migrate(message="Production migration")
    upgrade()
