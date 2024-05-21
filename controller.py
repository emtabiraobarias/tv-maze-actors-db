from flask_restx import Resource, Namespace
from helper import TVMaze_API_Access

ns_actor = Namespace('Actors', description='actor related operations')

### payloads
actor_create_payload = ns_actor.parser()
actor_create_payload.add_argument('name', type=str, location='args', help='actor name')
### payloads

@ns_actor.route('/')
class Actors(Resource):
    
    @ns_actor.expect(actor_create_payload)
    @ns_actor.response(201, 'Report created')
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
            return actor.json(), 201