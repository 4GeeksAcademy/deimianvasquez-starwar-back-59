"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planet, Favorite
import requests
# from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
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


@app.route("/people/population", methods=["GET"])
def people_population():
    url_people = "https://www.swapi.tech/api/people?page=1&limit=10"

    response = requests.get(url_people)
    data = response.json()

    for person in data["results"]:
        person_details = requests.get(person["url"])
        person_data = person_details.json()
        name = person_data["result"]["properties"]["name"]
        height = person_data["result"]["properties"]["height"]
        mass = person_data["result"]["properties"]["mass"]
        gender = person_data["result"]["properties"]["gender"]
        birth_year = person_data["result"]["properties"]["birth_year"]

        new_person = People(name=name, height=height, mass=mass,
                            gender=gender, birth_year=birth_year)
        db.session.add(new_person)
    try:
        db.session.commit()
        return jsonify("People added successfully"), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route("/planet/population", methods=["GET"])
def planet_population():
    url_planets = "https://www.swapi.tech/api/planets?page=1&limit=10"

    response = requests.get(url_planets)
    data = response.json()

    for planet in data["results"]:
        planet_details = requests.get(planet["url"])
        planet_data = planet_details.json()
        name = planet_data["result"]["properties"]["name"]
        climate = planet_data["result"]["properties"]["climate"]
        population = planet_data["result"]["properties"]["population"]
        terrain = planet_data["result"]["properties"]["terrain"]

        new_planet = Planet(name=name, climate=climate,
                            population=population, terrain=terrain)
        db.session.add(new_planet)
    try:
        db.session.commit()
        return jsonify("Planets added successfully"), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route('/people', methods=['GET'])
def get_people():
    people = People.query.all()
    people_serialized = [person.serialize() for person in people]
    return jsonify(people_serialized), 200


@app.route('/people/<int:person_id>', methods=['GET'])
def get_person(person_id):
    person = People.query.get(person_id)
    if person is None:
        return jsonify({"error": "Person not found"}), 404
    return jsonify(person.serialize()), 200


@app.route('/planet', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    planets_serialized = [planet.serialize() for planet in planets]
    return jsonify(planets_serialized), 200


@app.route('/planet/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify({"error": "Planet not found"}), 404
    return jsonify(planet.serialize()), 200


@app.route('/user', methods=['GET'])
def get_users():
    users = User.query.all()
    users_serialized = [user.serialize() for user in users]
    return jsonify(users_serialized), 200


@app.route("/user/favorites", methods=["GET"])
def get_user_favorites():
    user_id = 1

    favorites = User.query.get(user_id).favorites
    favorites_serialized = [favorite.serialize() for favorite in favorites]
    return jsonify(favorites_serialized), 200
    # favorites_serialized = []
    # for favorite in favorites:
    #     if favorite.people:
    #         favorites_serialized.append({
    #             "id": favorite.id,
    #             "type": "people",
    #             "name": favorite.people.name
    #         })
    #     elif favorite.planet:
    #         favorites_serialized.append({
    #             "id": favorite.id,
    #             "type": "planet",
    #             "name": favorite.planet.name
    #         })

    return jsonify(favorites_serialized), 200


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
