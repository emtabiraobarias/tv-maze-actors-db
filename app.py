from flask import Flask
from flask_restx import Api

import os
os.environ['DATABASE_URL'] = 'sqlite:///tv-maze-actors.db'

from tv_maze_db_api import app

if __name__ == '__main__':
    app.run(debug=True)