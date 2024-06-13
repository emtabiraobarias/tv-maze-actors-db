# tv-maze-actors-db
Demonstration of data services engineering through creating REST API services from a database repository

## What is this about?
A Flask-Restx data service that allows a client to read and store information about actors/actresses, and allows the consumers to access the data through a REST API. The source data is retrieved from *TV Maze API* source URL [http://api.tvmaze.com/] with added functionalities that would require saving to an external (local) database.

## Set up instructions
### Setting up the VirtualEnv and install dependencies
First you need to set up the python virtual environment using `pipenv` and install all the dependencies:
```
# create the virtual environment and activate it in your current shell
pipenv shell

# install all the dependencies found in Pipfile
pipenv install

# run the flask-restx application
python app.py

# You can get the DB API resource endpoints and schema payloads through Swagger-UI
# Open the browser and navigate to http://127.0.0.1:5000/
```
A sqlite db named *tv-maze-actors.db* will be created under the `instance` directory. This will also run the web service on port 5000.

## Feature checklist
[x] Add a new actor [x] Unit test

[x] Retrieve an actor [x] Unit test

[x] Delete an actor [x] Unit test

[x] Update an actor [ ] Unit test

[x] Retrieve list of available actors [ ] Unit test

[x] Get statistics of existing actors [ ] Unit test


## Testing instructions
TBA
```
pytest --cov=test  
```
