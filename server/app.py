#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from flask import make_response

from config import app, db, api
from models import User, Recipe
import ipdb

class Signup(Resource):
    def post(self):
        response = request.get_json()

        try:
            user = User(
                username=response["username"],
                image_url=response["image_url"],
                bio=response["bio"]
            )

            user.password_hash = response["password"]

            db.session.add(user)
            db.session.commit()

            return make_response(user.to_dict(), 201)
        except:
            return make_response({}, 422)

class CheckSession(Resource):
    def get(self):
        user_id = session["user_id"]
        if user_id:
            user = User.query.filter_by(id = user_id).first().to_dict()
            return make_response(user, 200)
        return {},401

class Login(Resource):
    def post(self):
        req_json = request.get_json()
        username = req_json["username"]
        password = req_json["password"]

        user = User.query.filter_by(username = username).first()

        try:
            user.authenticate(password)
            session["user_id"] = user.id
            user = user.to_dict()
            return make_response(user, 200)
        except:
            return {}, 401


class Logout(Resource):
    def delete(self):    
        if session["user_id"]:
            session["user_id"] = None
            return {}, 204
        
        return {}, 401


class RecipeIndex(Resource):
    def get(self):
        user = User.query.filter_by(id = session["user_id"]).first()
        if user:
            return make_response(user.to_dict()["recipes"], 200)
        else:
            return make_response({"message": "Error, user not logged in"}, 401)
        
    def post(self):

        if not session["user_id"]:
            return {}, 401

        user = User.query.filter_by(id=session["user_id"]).first()
        req_json = request.get_json()

        try:
            recipe = Recipe(
                title=req_json["title"],
                instructions=req_json["instructions"],
                minutes_to_complete=req_json["minutes_to_complete"],
            )
            user.recipes.append(recipe)
            db.session.add(recipe, user)
            db.session.commit()
            return make_response(recipe.to_dict(), 201)
        except:
            return {}, 422



api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)