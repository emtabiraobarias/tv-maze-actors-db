# reference: https://www.linkedin.com/pulse/unit-testing-flask-application-gitau-harrison/
import os
import datetime as dt
os.environ['DATABASE_URL'] = 'sqlite:///test.db'

from tv_maze_db_api import app, db, api, controller, model
import unittest

class TestDatabaseFeatures(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app_ctxt = self.app.app_context()
        #db.init_app(self.app)
        with self.app_ctxt:
            db.create_all()
        self.app_ctxt.push()
        self.client = self.app.test_client()

    def tearDown(self):
        with self.app_ctxt:
            db.drop_all()
        self.app_ctxt.pop()
        self.app = None
        self.app_ctxt = None

    def test_app(self):
        assert self.app is not None
        assert app == self.app 

    def test_app_page(self):
        response = self.client.get('/', follow_redirects=True)
        assert response.status_code == 200

    def test_should_add_actor(self):
        response = self.client.post('/actors/?name=Brad Pitt', follow_redirects=True)
        assert response.status_code == 201
        html = response.get_data(as_text=True)
        assert '"id": 1' in html
        assert '"last-update": "', dt.datetime.now().strftime('%Y-%m-%d') in html
        assert '"_links": {"self": {"href": "http://localhost/db/actors/1"}}}' in html

    
        


if __name__ == '__main__':
    print('I was in test')
    unittest.main()