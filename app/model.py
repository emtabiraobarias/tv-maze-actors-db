import datetime as dt
import pandas as pd
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

    def json(self):
        return {
            'id': self.id,
            'name': self.name
        }

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
            'id': self.actor_id,
            'name': self.name, 
            'country': self.country,
            'gender': self.gender,
            'last_update': str(self.last_update),
            'birthday': str(self.birthday),
            'deathday': str(self.deathday)
        }

    def created_json(self):
        return {
            'id': self.id, 
            'last-update': str(self.last_update), 
            '_links': { 
                'self': { 
                    'href': 'http://' + request.host + '/db/actors/' + str(self.id)
                } 
            }
        }
    
    def get_json(self, prev_actor, next_actor):
        return {
            'id': self.id, 
            'last_update':self.last_update.strftime('%m-%d-%Y %H:%M:%S'), 
            'name': self.name,
            'country': None if not self.country else self.country,
            'gender': None if not self.gender else self.gender,
            'birthday': None if not self.birthday else self.birthday.strftime('%m-%d-%Y'),
            'deathday': None if not self.deathday else self.deathday.strftime('%m-%d-%Y'),
            'links': { 
                'self': { 
                    'href': 'http://' + request.host + '/actors/' + str(self.id)
                }, 
                'previous': { 
                    'href': None if not prev_actor else 'http://' + request.host + '/actors/' + str(prev_actor.id)
                },
                'next': { 
                    'href': None if not next_actor else 'http://' + request.host + '/actors/' + str(next_actor.id)
                } 
            }, 
            'shows': list(map(lambda n: n.name, self.shows))
        }

    def deleted_json(self, id):
        return { 
            'message': 'The actor with id {} was removed from the database!'.format(id),
            'id' : id
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
    
    @staticmethod
    def actor_list_json(actors: List,
                    page: int, 
                    size: int, 
                    stop: int, 
                    total_actors: int, 
                    order: str, 
                    filter: str,
        ):
        actors_list = [] 
        for actor in actors:
            actor_dict = actor._asdict()
            #for some reason the Actor object is being passed, so have to remove it for JSON to deserialise
            del actor_dict['Actor'] 
            actors_list.append(actor_dict)
        print(actors_list)
        return {
            'page': page,
            'page-size': size,
            'actors': actors_list,
            '_links': {
                'self': {
                    'href': 'http://' + request.host + '/actors?order={}&page={}&size={}&filter={}'.format(order,page,size,filter)
                },
                'next': {
                    'href': None if not stop < total_actors else 'http://' + request.host + '/actors?order={}&page={}&size={}&filter={}'.format(order,page+1,size,filter)
                }
            }
        }
    
    @classmethod
    def find_by_actorid(cls, _userid: int) -> "Actor":
        return cls.query.filter_by(actor_id=_userid).first()
    
    @classmethod
    def find_by_id(cls, _id: int) -> "Actor":
        return cls.query.filter_by(id=_id).first()
    
    @classmethod
    def get_prev_id(cls, _id: int) -> "Actor":
        return cls.query.order_by(cls.id.desc()).filter(cls.id < _id).first()
    
    @classmethod
    def get_next_id(cls, _id: int) -> "Actor":
        return cls.query.order_by(cls.id.asc()).filter(cls.id > _id).first()
    
    @classmethod
    def get_all(cls) -> List["Actor"]:
        return cls.query.all()
    
    @classmethod
    def filter_and_sort_columns_with_pagination(cls, _sort: str, _select: str, _start: int, _stop: int) -> List["Actor"]:
        query = db.session.query(Actor)
        select_columns = _select.split(',')
        for column in select_columns:
            query = query.add_columns(db.Column(column))
        sort_columns = _sort.split(',')
        for clause in sort_columns:
            isDescending = clause[0] == '-' # ascending by default is nothing was specified
            column = clause[1:]
            sort = db.desc(column) if isDescending else db.asc(column)
            query = query.order_by(sort)
        query = query.slice(_start, _stop) # apply pagination, stop is exclusive
        return query.all()
    
    @classmethod
    def count_by_last_updated(cls, _timedelta:int) -> int:
        return cls.query.filter(cls.last_update > _timedelta).count()
    
    def save_to_db(self) -> None:
        # prevent duplicate entries
        try:
            db.session.add(self)
            db.session.commit()
            db.session.flush()
        except Exception as msg:
            db.session.rollback()
            print("ERROR saving actor entity: " + str(msg))

    def delete_from_db(self) -> None:
        try:
            db.session.delete(self)
            db.session.commit()
            db.session.flush()
        except Exception as msg:
            db.session.rollback()
            print("ERROR deleting actor entity: " + str(msg))
            raise Exception(str(msg))

    