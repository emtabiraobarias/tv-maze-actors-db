import datetime as dt
from flask import request
from db import db
from typing import List

show_actor_association_table = db.Table('show_actor_association', db.Model.metadata,
        db.Column('show_id', db.ForeignKey('tv_shows.id')),
        db.Column('actor_id', db.ForeignKey('actors.id'))
    )

class Show(db.Model):
    __tablename__ = 'tv_shows'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    def __init__(self, name):
        self.name = name

    @classmethod
    def find_by_showname(cls, _show_name: str) -> "Show":
        return cls.query.filter_by(name = _show_name).first()


class Actor(db.Model):
    __tablename__ = 'actors'
    id = db.Column(db.Integer, primary_key=True)
    actor_id = db.Column(db.Integer, unique=True)
    name = db.Column(db.String)
    country = db.Column(db.String)
    gender = db.Column(db.String)
    last_update = db.Column(db.DateTime, default=dt.datetime.now())
    birthday = db.Column(db.Date)
    deathday = db.Column(db.Date)
    shows = db.relationship("Show", secondary=show_actor_association_table, cascade="all, delete")
    
    def __init__(self, actor_id, name, country, gender, birthday, deathday):
        self.actor_id = actor_id
        self.name = name
        self.country = country
        self.gender = gender
        self.last_update = dt.datetime.now()
        self.birthday = birthday
        self.deathday = deathday
        
    def json(self):
        return {
            'id': self.id, 
            'last-update': str(self.last_update), 
            '_links': { 
                'self': { 
                    'href': 'http://' + request.host + '/db/actors/' + str(self.id)
                } 
            }
        }

    @staticmethod
    def from_json(json_dict):
        print(json_dict)
        return Actor(
            actor_id = json_dict['id'],
            name = json_dict['name'],
            country = None if not json_dict['country'] else json_dict['country']['name'],
            gender = None if not json_dict['gender'] else json_dict['gender'],
            birthday = None if not json_dict['birthday'] else dt.datetime.strptime(json_dict['birthday'], "%Y-%m-%d").date(),
            deathday = None if not json_dict['deathday'] else dt.datetime.strptime(json_dict['deathday'], "%Y-%m-%d").date()
        )
    
    @classmethod
    def find_by_actorid(cls, _userid: int) -> "Actor":
        return cls.query.filter_by(actor_id=_userid).first()
    
    def save_to_db(self) -> None:
        # prevent duplicate entries
        try:
            db.session.add(self)
            db.session.commit()
            db.session.flush()
        except Exception as msg:
            db.session.rollback()
            print("ERROR saving actor entity: " + str(msg))

    