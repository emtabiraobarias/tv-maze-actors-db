from flask_restx import Resource, Namespace
from helper import TVMaze_API_Access
from model import Actor

ns_actor = Namespace('Actors', description='actor related operations')

### payloads
actor_create_payload = ns_actor.parser()
actor_create_payload.add_argument('name', type=str, location='args', help='actor name')
### payloads

@ns_actor.route('/')
class Actors(Resource):
    
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
            return 'There was an error in processing: {}.'.format(msg), 400
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