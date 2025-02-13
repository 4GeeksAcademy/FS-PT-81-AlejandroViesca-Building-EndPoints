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
from models import db, Users, Planets, Persons, Favourite_persons, Favourite_planets
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


# _________________________________________USER_________________________________________

@app.route('/users', methods=['GET'])  # _____GET_____
def get_users():
    try:
        data = Users.query.all()
        data = [user.serialize() for user in data]

        return jsonify({"msg": "GET User", "data": data}), 200
    
    except Exception as e:
        return jsonify({"msg": "Error in GET Users", "error": str(e)}), 500
    

@app.route('/users/<int:id>', methods=['GET'])  # _____GET ID_____
def get_one_user(id):
    try:
        data = Users.query.get(id)
        if not data:
            return jsonify({"msg": "User not found"}), 404
        
        return jsonify({"msg": "One user with id: " + str(id), "user": data.serialize()}), 200
    
    except Exception as e:
        return jsonify({"msg": "Error in GET User", "error": str(e)}), 500
    

@app.route('/users/<int:id>/favourites', methods=['GET'])  # _____GET USER FAVOURITES_____
def get_user_favourites(id):
    try:
        user = Users.query.get(id)
        if not user:
            return jsonify({"msg": "User not found"}), 404

        fav_persons = Favourite_persons.query.filter_by(id=id).all()
        fav_planets = Favourite_planets.query.filter_by(id=id).all()

        fav_persons_data = [fav.serialize() for fav in fav_persons] if fav_persons else []
        fav_planets_data = [fav.serialize() for fav in fav_planets] if fav_planets else []

        return jsonify({
            "msg": f"Favourites for user {id}",
            "favourite_persons": fav_persons_data,
            "favourite_planets": fav_planets_data
        }), 200
    
    except Exception as e:
        return jsonify({"msg": "Error in GET User Favourites", "error": str(e)}), 500

    
@app.route('/users', methods=['POST'])  # _____POST_____
def create_user():
    try:
        name = request.json.get('name', None)
        if not name:
            return jsonify({"msg": "Name is required"}), 400
        
        check = Users.query.filter_by(name=name).first()
        if check:
            return jsonify({"msg": "This user already exists"}), 400

        new_user = Users(name=name)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"msg": "User created successfully", "data": new_user.serialize()}), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Error in POST User", "error": str(e)}), 500
    

@app.route('/users/<int:id>', methods=['PUT'])  # _____PUT_____
def update_user(id):
    try:
        data = Users.query.get(id)
        if not data:
            return jsonify({"msg": "User not found"}), 404

        name = request.json.get('name', data.name)

        data.name = name

        db.session.commit()

        return jsonify({"msg": "User updated successfully", "data": data.serialize()}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Error in PUT User", "error": str(e)}), 500
    

@app.route('/users/<int:id>', methods=['DELETE'])  # _____DELETE_____
def delete_user(id):
    try:
        data = Users.query.get(id)
        if not data:
            return jsonify({"msg": "User not found"}), 404

        db.session.delete(data)
        db.session.commit()

        return jsonify({"msg": "User deleted successfully with id " + str(id)}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Error in DELETE User", "error": str(e)}), 500



# ________________________________________PERSON________________________________________

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



# ________________________________________PLANETS________________________________________

@app.route('/planets', methods=['GET'])  # _____GET_____
def get_planets():
    try:
        data = Planets.query.all()
        data = [planet.serialize() for planet in data]

        return jsonify({"msg": "GET Planets", "data": data}), 200
    
    except Exception as e:
        return jsonify({"msg": "Error in GET Planets", "error": str(e)}), 500


@app.route('/planets/<int:id>', methods=['GET'])  # _____GET ID_____
def one_planet(id):
    try:
        data = Planets.query.get(id)
        if not data:
            return jsonify({"msg": "Planet not found"}), 404
        
        return jsonify({"msg": "GET One Planet with ID: " + str(id), "planet": data.serialize()}), 200
    
    except Exception as e:
        return jsonify({"msg": "Error in GET ID Planet", "error": str(e)}), 500


@app.route('/planets', methods=['POST'])  # _____POST_____
def create_planet():
    try:
        name = request.json.get('name', None)
        if not name:
            return jsonify({"msg": "Name is required"}), 400
        
        check = Planets.query.filter_by(name=name).first()
        if check:
            return jsonify({"msg": "This planet already exists"}), 400

        new_planet = Planets(name=name)

        db.session.add(new_planet)
        db.session.commit()

        return jsonify({"msg": "Planet created", "data": new_planet.serialize()}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Error in POST Planet", "error": str(e)}), 500


@app.route('/planets/<int:id>', methods=['PUT'])  # _____PUT_____
def update_planet(id):
    try:
        data = Planets.query.get(id)
        if not data:
            return jsonify({"msg": "Planet not found"}), 404

        name = request.json.get('name', data.name)
        
        data.name = name

        db.session.commit()

        return jsonify({"msg": "Planet updated", "data": data.serialize()}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Error in PUT Planet", "error": str(e)}), 500


@app.route('/planets/<int:id>', methods=['DELETE'])  # _____DELETE_____
def delete_planet(id):
    try:
        data = Planets.query.get(id)
        if not data:
            return jsonify({"msg": "Planet not found"}), 404
        
        db.session.delete(data)
        db.session.commit()

        return jsonify({"msg": "Planet deleted with id " + str(id)}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Error in DELETE Planet", "error": str(e)}), 500



# ________________________________________FAVOURITE_PERSON________________________________________

@app.route('/favourite/person', methods=['GET'])  # _____GET_____
def get_fav_persons():
    try:
        data = Favourite_persons.query.all()
        data = [fav_person.serialize() for fav_person in data]

        return jsonify({"msg": "GET Fav Persons", "data": data}), 200
    
    except Exception as e:
        return jsonify({"msg": "Error in GET Fav Person", "error": str(e)}), 500


@app.route('/favourite/person/<int:id>', methods=['GET'])  # _____GET ID_____
def one_fav_person(id):
    try:
        data = Favourite_persons.query.get(id)
        if not data:
            return jsonify({"msg": "Fav Person not found"}), 404
        
        return jsonify({"msg": "GET One Fav Person with ID: " + str(id), "fav_person": data.serialize()}), 200
    
    except Exception as e:
        return jsonify({"msg": "Error in GET ID Fav Person", "error": str(e)}), 500


@app.route('/favourite/person', methods=['POST'])  # _____POST_____
def create_fav_person():
    try:
        user_id = request.json.get('user_id', None)
        person_id = request.json.get('person_id', None)

        exists = Favourite_persons.query.filter_by(user_id= user_id, person_id=person_id).first()
        
        if exists: 
            return jsonify({"msg": "El personaje ya ha sido agregado a fovoritos"}), 400
        
        user_exists = Users.query.filter_by(id=user_id).first()
        if not user_exists: 
            return jsonify({"msg": "este usuario no existe"}), 400

        person_exists = Persons.query.filter_by(id=person_id).first()
        if not person_exists: 
            return jsonify({"msg": "este personaje no existe"}), 400

        new_fav_person = Favourite_persons(user_id= user_id, person_id=person_id)

        db.session.add(new_fav_person)
        db.session.commit()

        return jsonify({"msg": "Person created", "data": new_fav_person.serialize()}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Error in POST Person", "error": str(e)}), 500


@app.route('/favourite/person/<int:id>', methods=['PUT'])  # _____PUT_____
def update_fav_person(id):
    try:
        data = Favourite_persons.query.get(id)

        if not data:
            return jsonify({"msg": "Fav Person not found"}), 404

        user_id = request.json.get('user_id', data.user_id)
        person_id = request.json.get('person_id', data.person_id)
        if not user_id or not person_id:
            return jsonify({"msg": "user_id and person_id cannot be empty"}), 400
        
        user_exists = Users.query.get(user_id)
        person_exists = Persons.query.get(person_id)
        if not user_exists or not person_exists:
            return jsonify({"msg": "Invalid user_id or person_id"}), 400
        
        data.user_id = user_id
        data.person_id = person_id

        db.session.commit()

        return jsonify({"msg": "Fav Person updated", "data": data.serialize()}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Error in PUT Fav Person", "error": str(e)}), 500


@app.route('/favourite/person/<int:id>', methods=['DELETE'])  # _____DELETE_____
def delete_fav_person(id):
    try:
        data = Favourite_persons.query.get(id)

        if not data:
            return jsonify({"msg": "Fav Person not found"}), 404
        
        db.session.delete(data)
        db.session.commit()

        return jsonify({"msg": "Fav Person deleted with id " + str(id)}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Error in DELETE Fav Person", "error": str(e)}), 500
    


# ________________________________________FAVOURITE_PLANET________________________________________

@app.route('/favourite/planet', methods=['GET'])  # _____GET_____
def get_fav_planets():
    try:
        data = Favourite_planets.query.all()
        data = [fav_planet.serialize() for fav_planet in data]

        return jsonify({"msg": "GET Fav Planets", "data": data}), 200
    
    except Exception as e:
        return jsonify({"msg": "Error in GET Fav Planets", "error": str(e)}), 500


@app.route('/favourite/planet/<int:id>', methods=['GET'])  # _____GET ID_____
def one_fav_planet(id):
    try:
        data = Favourite_planets.query.get(id)
        if not data:
            return jsonify({"msg": "Fav Planet not found"}), 404
        
        return jsonify({"msg": "GET One Fav Planet with ID: " + str(id), "fav_planet": data.serialize()}), 200
    
    except Exception as e:
        return jsonify({"msg": "Error in GET ID Fav Planet", "error": str(e)}), 500


@app.route('/favourite/planet', methods=['POST'])  # _____POST_____
def create_fav_planet():
    try:
        user_id = request.json.get('user_id', None)
        planet_id = request.json.get('planet_id', None)

        exists = Favourite_planets.query.filter_by(user_id=user_id, planet_id=planet_id).first()
        if exists: 
            return jsonify({"msg": "El planeta ya ha sido agregado a favoritos"}), 400
        
        user_exists = Users.query.get(user_id)
        if not user_exists: 
            return jsonify({"msg": "Este usuario no existe"}), 400

        planet_exists = Planets.query.get(planet_id)
        if not planet_exists: 
            return jsonify({"msg": "Este planeta no existe"}), 400

        new_fav_planet = Favourite_planets(user_id=user_id, planet_id=planet_id)

        db.session.add(new_fav_planet)
        db.session.commit()

        return jsonify({"msg": "Fav Planet created", "data": new_fav_planet.serialize()}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Error in POST Fav Planet", "error": str(e)}), 500


@app.route('/favourite/planet/<int:id>', methods=['PUT'])  # _____PUT_____
def update_fav_planet(id):
    try:
        data = Favourite_planets.query.get(id)

        if not data:
            return jsonify({"msg": "Fav Planet not found"}), 404

        user_id = request.json.get('user_id', data.user_id)
        planet_id = request.json.get('planet_id', data.planet_id)
        if not user_id or not planet_id:
            return jsonify({"msg": "user_id and planet_id cannot be empty"}), 400
        
        user_exists = Users.query.get(user_id)
        planet_exists = Planets.query.get(planet_id)
        if not user_exists or not planet_exists:
            return jsonify({"msg": "Invalid user_id or planet_id"}), 400
        
        data.user_id = user_id
        data.planet_id = planet_id

        db.session.commit()

        return jsonify({"msg": "Fav Planet updated", "data": data.serialize()}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Error in PUT Fav Planet", "error": str(e)}), 500


@app.route('/favourite/planet/<int:id>', methods=['DELETE'])  # _____DELETE_____
def delete_fav_planet(id):
    try:
        data = Favourite_planets.query.get(id)

        if not data:
            return jsonify({"msg": "Fav Planet not found"}), 404
        
        db.session.delete(data)
        db.session.commit()

        return jsonify({"msg": "Fav Planet deleted with id " + str(id)}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Error in DELETE Fav Planet", "error": str(e)}), 500




# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
