from flask import Flask
# An extension for Flask to handle database operations
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource, reqparse, fields, marshal_with, abort

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)  # Create an instance of SQLAlchemy tied to the Flask app.
api = Api(app)  # API instance that will manage the routes

# Response formatting
userFields = {
    'id': fields.Integer,
    'name': fields.String,
    'email': fields.String
}
# fields.Integer and fields.String are provided by Flask-RESTful to help serialize the output into JSON format.

# Structure of the database table for users


class UserModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)

    # Define how to represent the object as a string
    def __repr__(self):
        return f'User(name= {self.name},email= {self.email})'


# Setting up the request argument parser for handling input data when creating or updating users
user_args = reqparse.RequestParser()
user_args.add_argument(
    'name', type=str, help='Name cannot be blank', required=True)
user_args.add_argument(
    'email', type=str, help='Email cannot be blank', required=True)


class Users(Resource):
    # This decorator will serialize the output into JSON format
    @marshal_with(userFields)
    def get(self):
        users = UserModel.query.all()
        return users

    @marshal_with(userFields)
    def post(self):
        args = user_args.parse_args()
        user = UserModel(name=args['name'], email=args['email'])
        db.session.add(user)
        db.session.commit()
        users = UserModel.query.all()
        return users, 201


class User(Resource):
    @marshal_with(userFields)
    def get(self, id):
        user = UserModel.query.filter_by(id=id).first()
        if not user:
            abort(404, message='User not found')
        return user

    @marshal_with(userFields)
    def patch(self, id):
        args = user_args.parse_args()
        user = UserModel.query.filter_by(id=id).first()
        if not user:
            abort(404, message='User not found')
        user.name = args['name']
        user.email = args['email']
        db.session.commit()
        return user

    @marshal_with(userFields)
    def delete(self, id):
        user = UserModel.query.filter_by(id=id).first()
        if not user:
            abort(404, message='User not found')
        db.session.delete(user)
        db.session.commit()
        return user, 200


api.add_resource(Users, '/api/users/')
api.add_resource(User, '/api/users/<int:id>')


@app.route('/')
def home():
    return '<h1> Flask REST API </h1>'


# Ensure that the Flask app runs when the script is executed directly
if __name__ == '__main__':
    app.run(debug=True)
