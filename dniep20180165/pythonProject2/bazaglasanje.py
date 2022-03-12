from flask_sqlalchemy import SQLAlchemy

databaseGlasanje = SQLAlchemy()


class Prijavljennaizborima(databaseGlasanje.Model):
    __tablename__ = "prijavljennaizborima"

    id = databaseGlasanje.Column(databaseGlasanje.Integer, primary_key=True)
    ucesnikID = databaseGlasanje.Column(databaseGlasanje.Integer, databaseGlasanje.ForeignKey("ucesnik.id"),
                                        nullable=False)
    izboriID = databaseGlasanje.Column(databaseGlasanje.Integer, databaseGlasanje.ForeignKey("izbori.id"),
                                       nullable=False)


class Ucesnik(databaseGlasanje.Model):
    __tablename__ = "ucesnik"
    id = databaseGlasanje.Column(databaseGlasanje.Integer, primary_key=True)
    name = databaseGlasanje.Column(databaseGlasanje.String(256), nullable=False)
    individual = databaseGlasanje.Column(databaseGlasanje.Boolean, nullable=False)
    izbori = databaseGlasanje.relationship("Izbori", secondary=Prijavljennaizborima.__table__, back_populates="ucesnik")

    def __repr__(self):
        return "({}, {}".format(self.id, self.name, self.individual)


class Izbori(databaseGlasanje.Model):
    __tablename__ = "izbori"
    id = databaseGlasanje.Column(databaseGlasanje.Integer, primary_key=True)
    start = databaseGlasanje.Column(databaseGlasanje.String(256), nullable=False)
    end = databaseGlasanje.Column(databaseGlasanje.String(256), nullable=False)
    individual = databaseGlasanje.Column(databaseGlasanje.Boolean, nullable=False)
    ucesnik = databaseGlasanje.relationship("Ucesnik", secondary=Prijavljennaizborima.__table__,
                                           back_populates="izbori")
    glasovi = databaseGlasanje.relationship("Glas", back_populates="izbori")
    def __repr__(self):
        return "({}, {} , {}".format(self.id, self.start, self.end, self.individual)


class Glas(databaseGlasanje.Model):
    __tablename__ = "glasovi"

    id = databaseGlasanje.Column(databaseGlasanje.Integer, primary_key=True)
    guid = databaseGlasanje.Column(databaseGlasanje.String(36), nullable=False)
    izboriid = databaseGlasanje.Column(databaseGlasanje.Integer, databaseGlasanje.ForeignKey("izbori.id"),
                                       nullable=False)
    kandidat = databaseGlasanje.Column(databaseGlasanje.Integer, nullable=False)
    validan = databaseGlasanje.Column(databaseGlasanje.Boolean, nullable=False)
    razlog = databaseGlasanje.Column(databaseGlasanje.String(256))
    jmbg = databaseGlasanje.Column(databaseGlasanje.String(13), nullable=False);
    izbori = databaseGlasanje.relationship("Izbori", back_populates="glasovi")

    def __repr__(self):
        return "{}, {}, {}".format(self.id, self.izboriid, self.kandidat)
