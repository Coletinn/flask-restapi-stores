from flask.views import MethodView
from flask_smorest import Blueprint, abort
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import create_access_token

from db import db
from models import UserModel
from schemas import UserSchema


blp = Blueprint("Users", "users", description="Operations on users")


@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserSchema)
    def post(self, data):
        if UserModel.query.filter(UserModel.username == data["username"]).first():
            abort(409, message="A user with that username already exists!")

        user = UserModel(
            username=data["username"],
            password=pbkdf2_sha256.hash(data["password"])
        )
        db.session.add(user)
        db.session.commit()

        return "User created successfully", 201



@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserSchema)
    def post(self, data):
        user = UserModel.query.filter(
            UserModel.username == data["username"]
        ).first()

        if user and pbkdf2_sha256.verify(data["password"], user.password):
            access_token = create_access_token(identity=user.id)
            return {"Access token": access_token}

        abort(401, message="Invalid credentials.")



@blp.route("/user/<int:user_id>")
class User(MethodView):
    @blp.response(200, UserSchema)
    def get(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        return user

    def delete(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return "User deleted", 201
