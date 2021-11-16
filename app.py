# app.py

from flask import Flask, request
from flask_restx import Api, Resource, reqparse
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
api = Api(app)
movie_ns = api.namespace('movies')
director_ns = api.namespace('directors')
genre_ns = api.namespace('genres')
parser = reqparse.RequestParser()
parser.add_argument('director_id', type=int)
parser.add_argument('genre_id', type=int)


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class MoviesSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Int()
    genre_id = fields.Int()
    director_id = fields.Int()


class DirectorsSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


class GenresSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


@movie_ns.route('/')
class MoviesView(Resource):
    @api.expect(parser)
    def get(self):
        movies_schema = MoviesSchema(many=True)
        director_id = parser.parse_args()['director_id']
        genre_id = parser.parse_args()['genre_id']
        if director_id and genre_id:
            movies = Movie.query.filter_by(director_id=director_id, genre_id=genre_id).all()
        elif director_id:
            movies = Movie.query.filter_by(director_id=director_id).all()
        elif genre_id:
            movies = Movie.query.filter_by(genre_id=genre_id).all()
        else:
            movies = Movie.query.all()
        if movies:
            return movies_schema.dump(movies), 200
        else:
            return "", 404

    def post(self):
        req_json = request.json
        new_movie = Movie(**req_json)
        with db.session.begin():
            db.session.add(new_movie)
        return "", 201


@movie_ns.route('/<int:uid>')
class MovieView(Resource):

    def get(self, uid: int):
        movie = Movie.query.get(uid)
        if movie:
            movie_schema = MoviesSchema()
            return movie_schema.dump(movie), 200
        else:
            return "", 404

    def put(self, uid: int):
        movie = Movie.query.get(uid)
        if movie:
            req_json = request.json
            movie.title = req_json.get("title")
            movie.description = req_json.get("description")
            movie.trailer = req_json.get("trailer")
            movie.year = req_json.get("year")
            movie.rating = req_json.get("rating")
            movie.genre_id = req_json.get("genre_id")
            movie.director_id = req_json.get("director_id")
            db.session.add(movie)
            db.session.commit()
            return "", 200
        else:
            return "", 404

    def delete(self, uid: int):
        movie = Movie.query.get(uid)
        if movie:
            db.session.delete(movie)
            db.session.commit()
            return "", 204
        else:
            return "", 404


@director_ns.route('/')
class DirectorsView(Resource):
    def get(self):
        directors_schema = DirectorsSchema(many=True)
        directors = Director.query.all()
        if directors:
            return directors_schema.dump(directors), 200
        else:
            return "", 404

    def post(self):
        req_json = request.json
        new_director = Director(**req_json)
        with db.session.begin():
            db.session.add(new_director)
        return "", 201


@director_ns.route('/<int:uid>')
class DirectorView(Resource):
    def get(self, uid: int):
        director = Director.query.get(uid)
        if director:
            directors_schema = DirectorsSchema()
            return directors_schema.dump(director), 200
        else:
            return "", 404

    def put(self, uid: int):
        director = Director.query.get(uid)
        if director:
            req_json = request.json
            director.name = req_json.get("name")
            db.session.add(director)
            db.session.commit()
            return "", 200
        else:
            return "", 404

    def delete(self, uid: int):
        director = Director.query.get(uid)
        if director:
            db.session.delete(director)
            db.session.commit()
            return "", 204
        else:
            return "", 404


@genre_ns.route('/')
class GenresView(Resource):
    def get(self):
        genres_schema = GenresSchema(many=True)
        genres = Genre.query.all()
        if genres:
            return genres_schema.dump(genres), 200
        else:
            return "", 404

    def post(self):
        req_json = request.json
        new_genre = Genre(**req_json)
        with db.session.begin():
            db.session.add(new_genre)
        return "", 201


@genre_ns.route('/<int:uid>')
class GenreView(Resource):
    def get(self, uid: int):
        genre = Genre.query.get(uid)
        if genre:
            genres_schema = GenresSchema()
            return genres_schema.dump(genre), 200
        else:
            return "", 404

    def put(self, uid: int):
        genre = Genre.query.get(uid)
        if genre:
            req_json = request.json
            genre.name = req_json.get("name")
            db.session.add(genre)
            db.session.commit()
            return "", 200
        else:
            return "", 404

    def delete(self, uid: int):
        genre = Genre.query.get(uid)
        if genre:
            db.session.delete(genre)
            db.session.commit()
            return "", 204
        else:
            return "", 404


if __name__ == '__main__':
    app.run(debug=True)
