"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from sqlalchemy import select
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Favourites, People, Planets
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

# enpoints de user
@app.route('/user', methods=['GET'])
def get_users():
    data = db.session.scalars(select(User)).all()
    results = list(map(lambda item: item.serialize(), data))
    if results == []:
        results = "there aren't any users in the database"
    response_body = {
        "result": results
    }
    return jsonify(response_body), 200

# enpoints de favourites
@app.route('/users/favorites', methods=['GET'])
def get_favourites():
    data = db.session.scalars(select(Favourites)).all()
    results = list(map(lambda favourite: favourite.serialize(), data))
    if results == []:
        results = "there aren't any favourites"
    response_body = {
        "results": results
    }
    return jsonify(response_body), 200

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favourite_planet(planet_id):
    request_data = request.json
    user_id = request_data["user_id"]
    try:
        planet = db.session.execute(db.select(Planets).filter_by(id=planet_id)).scalar_one()
    except NoResultFound:
        return jsonify({"error": "planet not found."}), 404
    try:
        user = db.session.execute(db.select(User).filter_by(id=user_id)).scalar_one()
    except NoResultFound:
        return jsonify({"error": "user not found"}), 404
    new_favourite = Favourites(
        users_favourites = user,
        planet_favourites = planet
    )
    db.session.add(new_favourite)
    db.session.commit()
    return jsonify(new_favourite.serialize()), 200

@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favourite_person(people_id):
    request_data = request.json
    user_id = request_data["user_id"]
    if "user_id" not in request_data:
        return jsonify({"error": "key user_id is obligatory."}), 400
    try:
        person = db.session.execute(db.select(People).filter_by(id=people_id)).scalar_one()
    except NoResultFound:
        return jsonify({"error": "person not found."}), 404
    try:
        user = db.session.execute(db.select(User).filter_by(id=user_id)).scalar_one()
    except NoResultFound:
        return jsonify({"error": "user not found"}), 404
    new_favourite = Favourites(
        users_favourites = user,
        people_favourites = person
    )
    db.session.add(new_favourite)
    db.session.commit()
    return jsonify(new_favourite.serialize()), 200

# enpoints de people
@app.route('/people', methods=['GET'])
def get_people():
    data = db.session.scalars(select(People)).all()
    print(data)
    results = list(map(lambda person: person.serialize(), data))
    response_body = {
        "results": results
    }
    return jsonify(response_body), 200


@app.route('/people/<int:people_id>', methods=['GET'])
def get_specific_users(people_id):
    try:
        person = db.session.execute(select(People).filter_by(id=people_id)).scalar_one()
    except NoResultFound:
        return jsonify({"error": "Person not found."}), 404
    result_body = {
        "result": person.serialize()
    }
    return jsonify(result_body), 200

# enpoints de planets
@app.route('/planets', methods=['GET'])
def get_planets():
    data = db.session.scalars(select(Planets)).all()
    results = list(map(lambda planet: planet.serialize(), data))
    result_body = {
        "results": results
    }
    return jsonify(result_body), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_specific_planet(planet_id):
    try:
        planet = db.session.execute(db.select(Planets).filter_by(id=planet_id)).scalar_one()
    except NoResultFound:
        return jsonify({"error": "Planet not found."}), 404
    response_body = {
        "results": planet.serialize()
    }
    return jsonify(response_body), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
