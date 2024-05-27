# reference: https://www.linkedin.com/pulse/unit-testing-flask-application-gitau-harrison/
import sys
import os
#basedir = os.path.abspath(os.path.dirname(__file__))
os.environ['DATABASE_URL'] = 'sqlite:///test.db'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tv_maze_db_api import app, db
#import tv_maze_db_api as tmdbapi
import unittest

class TestDatabaseFeatures(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app_ctxt = self.app.app_context()
        self.app_ctxt.push()
        #with self.app_ctxt:
        #db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        #with self.app_ctxt:
        db.drop_all()
        self.app_ctxt.pop()
        self.app = None
        self.app_ctxt = None

    def test_app(self):
        assert self.app is not None
        assert app == self.app 

    def test_should_add_actor(self):
        response = self.client.post('/actors/?name=Brad Pitt', data={
            'name': 'Brad Pitt'
        }, follow_redirects=True)
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        print(html)


if __name__ == '__main__':
    unittest.main()