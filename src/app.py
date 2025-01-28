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
@app.route('/users', methods=['GET'])
def get_users():
    data = db.session.scalars(select(User)).all()
    results = list(map(lambda item: item.serialize(), data))
    if results == []:
        results = "there aren't any users in the database"
    response_body = {
        "result": results
    }
    return jsonify(response_body), 200

@app.route('/user', methods=['POST'])
def add_user():
    request_data = request.json
    email = request_data.get("email")
    required_fields = ["email", "password"]
    for item in required_fields:
        if item not in request_data:
            return jsonify({"error": f"required field {item} missing"})
    try:
        existing_user = db.session.execute(db.select(User).filter_by(email=email.lower())).scalar_one()
        if existing_user:
            return ({"error": f"the user {email} already exists"}), 400
    except:
        None
    new_user= User(
        email=email,
        password=request_data.get("password")
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"results": new_user.serialize()}), 200

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
    if "user_id" not in request_data:
        return jsonify({"error": "key user_id is obligatory."}), 400
    user_id = request_data["user_id"]
    try:
        planet = db.session.execute(db.select(Planets).filter_by(id=planet_id)).scalar_one()
    except NoResultFound:
        return jsonify({"error": "planet not found."}), 404
    try:
        user = db.session.execute(db.select(User).filter_by(id=user_id)).scalar_one()
    except NoResultFound:
        return jsonify({"error": "user not found"}), 404
    try:
        favourite_exist = db.session.execute(db.select(Favourites).filter_by(users_favourites_id=user_id, planet_favourites_id=planet_id)).scalar_one()
        if favourite_exist:
            return jsonify({"msg": f"the user with id {user_id} already has the person with id {planet_id} as a favourite"}), 400
    except:
        None
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
    if "user_id" not in request_data:
        return jsonify({"error": "key user_id is obligatory."}), 400
    user_id = request_data["user_id"]
    try:
        person = db.session.execute(db.select(People).filter_by(id=people_id)).scalar_one()
    except NoResultFound:
        return jsonify({"error": "person not found."}), 404
    try:
        user = db.session.execute(db.select(User).filter_by(id=user_id)).scalar_one()
    except NoResultFound:
        return jsonify({"error": "user not found"}), 404
    try:
        favourite_exist = db.session.execute(db.select(Favourites).filter_by(users_favourites_id=user_id, people_favourites_id=people_id)).scalar_one()
        if favourite_exist:
            return jsonify({"msg": f"the user with id {user_id} already has the person with id {people_id} as a favourite"}), 400
    except:
        None
    new_favourite = Favourites(
        users_favourites = user,
        people_favourites = person
    )
    db.session.add(new_favourite)
    db.session.commit()
    return jsonify(new_favourite.serialize()), 200

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favourite_planet(planet_id):
    try:
        planet = db.session.execute(db.select(Favourites).filter_by(id=planet_id)).scalar_one()
    except NoResultFound:
        return jsonify({"error": "favourite planet not found"}), 404
    if planet.serialize()["planets"] == None:
        return jsonify({"error": "favourite planet not found"}), 404
    db.session.delete(planet)
    db.session.commit()
    return jsonify({"msg": "favourite planet deleted"}), 200


@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favourite_character(people_id):
    try:
        person = db.session.execute(db.select(Favourites).filter_by(id=people_id)).scalar_one()
    except NoResultFound:
        return jsonify({"error": "favourite person not found"}), 404
    if person.serialize()["people"] == None:
        return jsonify({"error": "favourite person not found"}), 404
    db.session.delete(person)
    db.session.commit()
    return jsonify({"msg": "favourite person deleted"}), 200


# enpoints de people
@app.route('/people', methods=['GET'])
def get_people():
    data = db.session.scalars(select(People)).all()
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


@app.route('/people', methods=['POST'])
def add_person():
    request_data = request.json
    if "name" not in request_data:
        return jsonify({"error": "name field is obligatory"}), 400
    name = request_data.get("name")
    data = db.session.scalars(select(People)).all()
    results = list(map(lambda person: person.serialize(), data))
    for person in results:
        if person["name"].lower() == name.lower():
            return jsonify({"error": f"{name} already exists"}), 400
    homeworld = None
    if request_data.get("homeworld_id"):
        homeworld_id = request_data.get("homeworld_id")
        try:
            homeworld = db.session.execute(db.select(Planets).filter_by(id=homeworld_id)).scalar_one()
        except NoResultFound:
            return jsonify({"error": "planet not found"}), 404
    new_person = People(
        name = request_data.get("name"),
        birth_year = request_data.get("birth_year"),
        eye_color = request_data.get("eye_color"),
        gender = request_data.get("gender"),
        hair_color = request_data.get("hair_color"),
        height = request_data.get("height"),
        weight = request_data.get("weight"),
        skin_color = request_data.get("skin_color"),
        species = request_data.get("species"),
        starships = request_data.get("starships"),
        vehicles = request_data.get("vehicles"),
        master = request_data.get("master"),
        disciple = request_data.get("disciple"),
        image = request_data.get("image"),
        films = request_data.get("films"),
        homeworld = homeworld
    )
    db.session.add(new_person)
    db.session.commit()
    return jsonify({"results": new_person.serialize()}), 200

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

# en revisión para que se vincule correctamente el resident con el people apropiado
@app.route('/planets', methods=['POST'])
def add_planet():
    request_data = request.json
    name = request_data.get("name")
    if "name" not in request_data:
        return jsonify({"error": "name field is obligatory"}), 400
    
    data = db.session.scalars(select(Planets)).all()
    results = list(map(lambda planet: planet.serialize(), data))
    for planet in results:
        if planet["name"].lower() == name.lower():
            return jsonify({"error": f"{name} already exists"}), 400
    residents = []
    if request_data.get("residents_id"):
        residents_id = request_data.get("residents_id")
        if not isinstance(residents_id, list):
            return jsonify({"error": "residents_id must be a list"}), 400
        try:
            residents = db.session.scalars(select(People).filter(People.id.in_(residents_id))).all()
        except NoResultFound:
            return jsonify({"error": "person not found"}), 404
    new_planet = Planets(
        name = request_data.get("name"),
        diameter = request_data.get("diameter"),
        rotation_period = request_data.get("rotation_period"),
        orbital_period = request_data.get("orbital_period"),
        gravity = request_data.get("gravity"),
        population = request_data.get("population"),
        climate = request_data.get("climate"),
        terrain = request_data.get("terrain"),
        surface_water = request_data.get("surface_water"),
        image = request_data.get("image"),
        species = request_data.get("species"),
        films = request_data.get("films"),
        residents = residents
    )
    db.session.add(new_planet)
    db.session.commit()
    return jsonify({"results": new_planet.serialize()}), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
