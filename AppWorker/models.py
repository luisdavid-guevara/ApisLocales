# models.py
from StartServer import db

class BaseConfiguration(db.Model):
    __tablename__ = 'base_configuration'
    id_configuration = db.Column(db.Integer, primary_key=True)
    cod_configuration = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False)

class BaseConfParameter(db.Model):
    __tablename__ = 'base_conf_parameter'
    id_conf_parameter = db.Column(db.Integer, primary_key=True)
    cod_configuration = db.Column(db.String(255), nullable=False)
    cod_parameter = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    value = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False)

