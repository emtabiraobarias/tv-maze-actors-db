import os
from flask import Flask
from flask_restx import Api
from .db import db
from .controller import ns_actor

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db.init_app(app)
with app.app_context():
    api = Api(app)
    api.add_namespace(ns_actor, path='/actors')
    db.create_all()
