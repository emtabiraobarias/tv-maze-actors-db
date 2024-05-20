from flask_sqlalchemy import SQLAlchemy
from flask import Flask, Blueprint, jsonify
from flask_restx import Api

db = SQLAlchemy()
app = Flask(__name__)
bluePrint = Blueprint('db', __name__, url_prefix='/db')
api = Api(app)
app.register_blueprint(bluePrint)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tv-maze-actors.db'

#@app.before_first_request
#def create_tables():
#    db.create_all()

if __name__ == '__main__':
    db.init_app(app)
    app.run(debug=True)