from geoalchemy2 import Geometry
from sqlalchemy.ext.declarative import declarative_base

from app.extensions import db

Base = declarative_base()


class Province(db.Model, Base):
    __tablename__ = "Province"

    id = db.Column(db.Integer, unique=True, primary_key=True, autoincrement=True)
    label = db.Column(db.String(64))
    area = db.Column(db.Numeric)
    geometry = db.Column(Geometry('POLYGON'))
