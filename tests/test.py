# reference: https://www.linkedin.com/pulse/unit-testing-flask-application-gitau-harrison/
import os
import datetime as dt
import json
import pytest
os.environ['DATABASE_URL'] = 'sqlite:///test.db'

from tv_maze_db_api import app, db, api, controller, model
import unittest

class TestDatabaseFeatures(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.app = app
        self.app_ctxt = self.app.app_context()
        #db.init_app(self.app)
        with self.app_ctxt:
            db.create_all()
        self.app_ctxt.push()
        self.client = self.app.test_client()

    @classmethod
    def tearDownClass(self):
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
        jsonresp = json.loads(html)
        assert jsonresp["id"] == 1
        assert jsonresp["last-update"].startswith(dt.datetime.now().strftime('%Y-%m-%d'))
        assert jsonresp["_links"]["self"]["href"] == "http://localhost/actors/1"

    def test_should_not_add_nonexistent_actor(self):
        response = self.client.post('/actors/?name=Bard Pitt', follow_redirects=True)
        assert response.status_code == 404
        html = response.get_data(as_text=True)
        assert 'Actor Bard Pitt cannot be found.' in html

    def test_should_retrieve_existing_actor(self):
        response = self.client.get('/actors/1', follow_redirects=True)
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        jsonresp = json.loads(html)
        assert jsonresp["id"] == 1
        assert jsonresp["name"] == "Brad Pitt"
        assert jsonresp["country"] == "United States"
        assert jsonresp["gender"] == "Male"
        assert jsonresp["last-update"].startswith(dt.datetime.now().strftime('%Y-%m-%d'))
        assert jsonresp["_links"]["self"]["href"] == "http://localhost/actors/1"

    def test_should_not_retrieve_nonexisting_actor(self):
        response = self.client.get('/actors/2', follow_redirects=True)
        assert response.status_code == 404
        html = response.get_data(as_text=True)
        assert 'Actor 2 does not exist.' in html
        


if __name__ == '__main__':
    print('I was in test')
    unittest.main()