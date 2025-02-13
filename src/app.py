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
from models import db, Users, Planets, Persons, Favourite_persons
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

# ____________________________PERSON____________________________

@app.route('/persons', methods=['GET'])  # _____GET_____
def get_persons():
    try:
        data = Persons.query.all()
        data = [person.serialize() for person in data]

        return jsonify({"msg": "GET Persons", "data": data}), 200
    
    except Exception as e:
        return jsonify({"msg": "Error in GET Person", "error": str(e)}), 500


@app.route('/persons/<int:id>', methods=['GET'])  # _____GET ID_____
def one_person(id):
    try:
        data = Persons.query.get(id)
        if not data:
            return jsonify({"msg": "Person not found"}), 404
        
        return jsonify({"msg": "GET One Person with ID: " + str(id), "person": data.serialize()}), 200
    
    except Exception as e:
        return jsonify({"msg": "Error in GET ID Person", "error": str(e)}), 500


@app.route('/persons', methods=['POST'])  # _____POST_____
def create_person():
    try:
        name = request.json.get('name', None)
        planet_id = request.json.get('planet_id', None)
        
        if not name or not planet_id:
            return jsonify({"msg": "All fields are required"}), 400
        
        check = Persons.query.filter_by(name=name).first()
        if check:
            return jsonify({"msg": "This person already exists"}), 400

        new_person = Persons(name=name, planet_id=planet_id)

        db.session.add(new_person)
        db.session.commit()

        return jsonify({"msg": "Person created", "data": new_person.serialize()}), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Error in POST Person", "error": str(e)}), 500


@app.route('/persons/<int:id>', methods=['PUT'])  # _____PUT_____
def update_person(id):
    try:
        data = Persons.query.get(id)

        if not data:
            return jsonify({"msg": "Person not found"}), 404

        name = request.json.get('name', data.name)
        planet_id = request.json.get('planet_id', data.planet_id)
        
        data.name = name
        data.planet_id = planet_id

        db.session.commit()

        return jsonify({"msg": "Person updated", "data": data.serialize()}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Error in PUT Person", "error": str(e)}), 500


@app.route('/persons/<int:id>', methods=['DELETE'])  # _____DELETE_____
def delete_person(id):
    try:
        data = Persons.query.get(id)

        if not data:
            return jsonify({"msg": "Person not found"}), 404
        
        db.session.delete(data)
        db.session.commit()

        return jsonify({"msg": "Person deleted with id " + str(id)}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Error in DELETE Person", "error": str(e)}), 500










@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
