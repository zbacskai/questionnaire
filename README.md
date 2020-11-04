# Questionnaire FLASK App

Simple FLASK implementation of a REST-API handling custom questionnaires with A/B(or c) testing
The Questions are stored in JSON format in MongoDB
The Questionnaires are stored in JSON format in MongoDB
The A/B test information is stored in Mongo
Session information(actual filled questionnaires) stored in Mongo DB

# Installation

## Docker Way

1.) install docker on your machine
2.) run `./build-image.sh`
3.) in directory `full-system` execute `docker-compose up`
4.) run `./bootstrap-db.sh`

After this:
the Mongo-express engine runs under: `http://localhsot:8081` (To explore data-strucures)

The actual Questionnaire API is accessible: `http://localhost:5000/`

## Development way

1.) install docker on machine
2.) in directory `devel-system` execute `docker-compose up`
3.) run `./bootstrap-db.sh`
4.) create a virual environment (python3.8, 3.9 was used for devel) `python -m venv .flask_env`
5.) activate environment `. .flask_env/bin/activate`
6.) Install requirements `pip install -r requirements.txt`
7.) Run application `make run`
8.) To run tests `make test_unit`

After this:
the Mongo-express engine runs under: `http://localhsot:8081` (To explore data-strucures)

The actual Questionnaire API is accessible: `http://localhost:5000/`

## Further Development

1.) Test coverage is really bad. Adding more unit-tests
2.) Adding validation of the JSON documents sent via the config API
3.) Adding erroe handling -> updating server response codes
4.) Further refactoring of the code
5.) Have a questionnaire compiler implemented as DB access is very intense and the flow can be pre-compiled into one document
6.) Adding a regression framework
7.) Introducing constants in the repo
8.) Document code
