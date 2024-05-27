from flask import Flask
from flask_restx import Api
from db import db
from controller import ns_actor

if __name__ == '__main__':
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tv-maze-actors.db'
    db.init_app(app)
    with app.app_context():
        api = Api(app)
        api.add_namespace(ns_actor, path='/actors')
        db.create_all()
        app.run(debug=True)