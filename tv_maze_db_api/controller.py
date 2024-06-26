import datetime as dt
import pandas as pd
from flask import Response
from flask_restx import Resource, Namespace
from .helper import TVMaze_API_Access, Statistics_Helper
from .model import Actor, Show

ns_actor = Namespace('Actors', description='actor related operations')

### payloads
actor_create_payload = ns_actor.parser()
actor_create_payload.add_argument('name', type=str, location='args', help='actor name')

actor_patch_payload = ns_actor.parser()
actor_patch_payload.add_argument('name', type=str, location='args', help='actor name')
actor_patch_payload.add_argument('country', type=str, location='args', help='actor birth country')
actor_patch_payload.add_argument('birthday', type=str, location='args', help='actor birth date')
actor_patch_payload.add_argument('deathday', type=str, location='args', help='actor death date')

actors_get_payload = ns_actor.parser()
actors_get_payload.add_argument('order', type=str, location='args', help='sorting method')
actors_get_payload.add_argument('page', type=int, location='args', help='page to display')
actors_get_payload.add_argument('size', type=int, location='args', help='size of page')
actors_get_payload.add_argument('filter', type=str, location='args', help='actor attributes to display')

actors_stats_payload = ns_actor.parser()
actors_stats_payload.add_argument('format', type=str, location='args', help='json or image return type')
actors_stats_payload.add_argument('by', type=str, location='args', help='actor attribute')
### payloads

@ns_actor.route('/')
class Actors(Resource):
    
    @ns_actor.expect(actors_get_payload)
    @ns_actor.doc("Get list of actors.")
    @ns_actor.response(404, 'No actors in the database')
    @ns_actor.response(400, 'Error retrieving actors from the database')
    def get(self):
        try:
            args = actors_get_payload.parse_args()
            page = 1 if args['page'] is None else args['page']
            size = 10 if args['size'] is None else args['size']
            filter = 'id,name' if args['filter'] is None else args['filter']
            order = '+id' if args['order'] is None else args['order']
            start = size * (page - 1)
            stop = page * size
            total_actors = len(Actor.get_all())
            if total_actors > 0:
                actors = Actor.filter_and_sort_columns_with_pagination(order, filter, start, stop)
                return Actor.actor_list_json(
                    actors, 
                    page, 
                    size, 
                    stop, 
                    total_actors, 
                    order, 
                    filter), 200
            else:
                return 'There are no actors in the database.', 404
        except Exception as msg:
            return 'There was an error in retrieving actors list: {}.'.format(msg), 400


    @ns_actor.doc("Add an actor to database.")
    @ns_actor.expect(actor_create_payload)
    @ns_actor.response(201, 'Actor created')
    @ns_actor.response(404, 'Actor not found')
    @ns_actor.response(400, 'Actor cannot be added')
    def post(self):
        try:
            # get name query parameter
            # ensure clean input data (convert special characters to space)
            args = actor_create_payload.parse_args()
            arg_name = args['name']
            api_access = TVMaze_API_Access('https://api.tvmaze.com/search/people?q=')
            actor = api_access.get_actor(arg_name)
        except Exception as msg:
            print('There was an error in processing: {}.'.format(msg))
        if actor is None:
            return 'Actor {} cannot be found.'.format(arg_name), 404
        else:
            actor.save_to_db()
            return actor.created_json(), 201
        

@ns_actor.route('/<int:id>')
class SingleActor(Resource):

    @ns_actor.doc("Get a single actor.")
    @ns_actor.response(404, 'Actor not found')
    def get(self, id):
        # get current actor
        actor = Actor.find_by_id(id)
        if actor is None:
            return 'Actor {} does not exist.'.format(id), 404
        # get previous actor
        prev_actor = Actor.get_prev_id(id)
        # get next actor
        next_actor = Actor.get_next_id(id)
        return actor.get_json(prev_actor=prev_actor, next_actor=next_actor), 200
    

    @ns_actor.response(200, 'Actor deleted')
    @ns_actor.response(404, 'Actor does not exist')
    @ns_actor.response(304, 'Unable to delete Actor')
    def delete(self, id):
        actor = Actor.find_by_id(id)
        if actor is None:
            return 'Actor {} does not exist.'.format(id), 404

        try:
            actor.delete_from_db()
            return actor.deleted_json(id=id), 200
        except Exception as msg:
            return "Actor {0} cannot be deleted. Reason: {1}".format(id, msg), 304
        
    
    @ns_actor.expect(actor_patch_payload)
    @ns_actor.response(200, 'Actor updated')
    @ns_actor.response(404, 'Actor does not exist')
    @ns_actor.response(304, 'Unable to update Actor')
    def patch(self, id):
        actor = Actor.find_by_id(id)
        if actor is None:
            return 'Actor {} does not exist.'.format(id), 404

        try:
            actor_payload = actor_patch_payload.parse_args()
            # update all properties for future flexibility
            name = country = deathday = birthday = shows = gender = None
            for key in actor_payload.keys():
                if key == 'name':
                    name = actor_payload[key]
                elif key == 'country':
                    country = actor_payload[key]
                elif key == 'gender':
                    gender = actor_payload[key]
                elif key == 'deathday':
                    deathday = actor_payload[key]
                elif key == 'birthday':
                    birthday = actor_payload[key]
                elif key == 'shows':
                    shows = actor_payload[key]
                    
            actor.name = actor.name if name is None else name
            actor.country = actor.country if country is None else country
            actor.gender = actor.gender if gender is None else gender
            actor.deathday = actor.deathday if deathday is None else dt.datetime.strptime(deathday, "%d-%m-%Y").date()
            actor.birthday = actor.birthday if birthday is None else dt.datetime.strptime(birthday, "%d-%m-%Y").date()
            
            if not shows is None:
                show_entities = []
                for show_name in shows:
                    existing_show = Show.find_by_showname(show_name)
                    if existing_show is None:
                        show_entities.append(Show(name = show_name))
                    else:
                        show_entities.append(existing_show)
            actor.shows = actor.shows if shows is None else show_entities
            actor.last_update = dt.datetime.now()
            actor.save_to_db()
            return actor.created_json(), 200
        except Exception as msg:
            return 'There was an error in processing. Item was not updated due to: {}.'.format(msg), 304
        

@ns_actor.route('/statistics')
class ActorsStats(Resource):
    
    @ns_actor.expect(actors_stats_payload)
    @ns_actor.doc("Get statistics of existing actors.")
    @ns_actor.response(404, 'No actors in the database')
    @ns_actor.response(400, 'Error retrieving statistics of actors from the database')
    def get(self):
        try:
            args = actors_stats_payload.parse_args()
            format = args['format']
            by = args['by']
            total_actors = len(Actor.get_all())
            # get actors updated count for the last 24 hours
            one_day_ago = dt.datetime.now() - dt.timedelta(hours=24)
            total_updated = Actor.count_by_last_updated(one_day_ago)
            # get all actors for stats
            all_actors = Actor.get_all()
            df = pd.DataFrame.from_records([a.json() for a in all_actors])
            # add life_status to the df
            df['life_status'] = df.apply(lambda x: "Alive" if x['deathday'] is None else "Dead", axis=1)
            # add birthday month to the df
            df['birth_month'] = pd.DatetimeIndex(df['birthday']).month_name()
            # add birthday year to the df
            df['birth_year'] = pd.DatetimeIndex(df['birthday']).year.astype('Int32').astype(str)
            # start group by processing
            by_param = by.lower().split(',')
            group_by_dict = {}
            for attr in by_param:
                # do group by statistics and compute percentage
                by_attr = 'by-' + attr
                if attr == 'birthday':
                    month_percentage = round(df['birth_month'].value_counts() / total_actors * 100, 1)
                    Statistics_Helper.build_group_dict(month_percentage, group_by_dict, by_attr + '_month')
                    year_percentage = round(df['birth_year'].value_counts() / total_actors * 100, 1)
                    Statistics_Helper.build_group_dict(year_percentage, group_by_dict, by_attr + '_year')
                else:
                    attr_percentage = round(df[attr].value_counts() / total_actors * 100, 1)
                    Statistics_Helper.build_group_dict(attr_percentage, group_by_dict, by_attr)

            # generate return info based on selected format
            if format.lower() == 'json':
                output = Statistics_Helper.generate_stats_json(total_actors=total_actors, total_updated=total_updated, group_by_dict=group_by_dict)
                return output, 200
            elif format.lower() == 'image':
                output = Statistics_Helper.generate_viz_image(group_by_dict=group_by_dict)
                return Response(output.getvalue(), mimetype='image/png')
            else:
                return 'Selected format is not accepted.', 400        

        except Exception as msg:
            return 'There was an error in processing: {}.'.format(msg), 400