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
from models import db, User, Character, Planet, Favorites
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


@app.route('/user', methods=['GET'])
def handle_hello():
    usuarios = User.query.all()
    if usuarios == []:
        return jsonify({"msg": "No existen usuarios"}), 404
    response_body = [usuario.serialize() for usuario in usuarios]
    return jsonify(response_body), 200


@app.route('/characters', methods=['GET'])
def get_characters():
    characters = Character.query.all()
    if characters == []:
        return jsonify({"msg": "No existen personajes"}), 404
    response_body = [character.serialize() for character in characters]
    return jsonify(response_body), 200


@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    if planets == []:
        return jsonify({"msg": "No existen planetas"}), 404
    response_body = [planet.serialize() for planet in planets]
    return jsonify(response_body), 200


@app.route('/characters/<int:id>', methods=['GET'])
def get_characters_id(id):
    character = Character.query.filter_by(id=id).first()
    if character == None:
        return jsonify({"msg": "No existe el personaje"}), 404
    return jsonify(character.serialize()), 200


@app.route('/planets/<int:id>', methods=['GET'])
def get_planets_id(id):
    planet = Planet.query.filter_by(id=id).first()
    if planet == None:
        return jsonify({"msg": "No existe el planeta"}), 404
    return jsonify(planet.serialize()), 200


@app.route('/favorites/planets/<int:planet_id>', methods=['POST'])
def post_planets_fav(planet_id):
    planet = Planet.query.filter_by(id=planet_id).first()
    if planet == None:
        return jsonify({"msg": "No existe el planeta"}), 404

    new_fav = Favorites(
        user_id=2,
        planet_id=planet_id,
    )
    db.session.add(new_fav)
    db.session.commit()
    return jsonify({"msg": "Nuevo favorito creado"}), 201


@app.route('/favorites/characters/<int:character_id>', methods=['POST'])
def post_characters_fav(character_id):
    character = Character.query.filter_by(id=character_id).first()
    if character == None:
        return jsonify({"msg": "No existe el personaje"}), 404

    new_fav = Favorites(
        user_id=2,
        character_id=character_id,
    )
    db.session.add(new_fav)
    db.session.commit()
    return jsonify({"msg": "Nuevo favorito creado"}), 201

@app.route('/favorites/user/<int:id>', methods=['GET'])
def get_user_fav(id):
    usuarios = Favorites.query.filter_by(user_id=id).all()
    if usuarios == []:
        return jsonify({"msg": "No tiene favoritos"}), 404
    
    response_body = [usuario.serialize() for usuario in usuarios]
    return jsonify(response_body), 200

@app.route('/favorites/<int:id>', methods=['DELETE'])
def delete_fav(id):
    favorite = Favorites.query.filter_by(id=id).first()
    if favorite == None:
        return jsonify({"msg": "No existe el favorito"}), 404
    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"msg": "Favorito eliminado"}), 204


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
