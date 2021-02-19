import os

from flask import render_template, request, url_for, jsonify, make_response
from flask_jwt_extended import create_access_token, jwt_required, current_user, create_refresh_token, get_jwt, get_jti
from flask_restful import fields, marshal, reqparse, Resource
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename

from api.mixins import ObjectResource, PaginatedListResource, OnlyJsonMixin
from api.models import Book, Author, User
from api.utils import decode_image


class BaseAuthorResource:
    model = Author

    parser = reqparse.RequestParser()
    parser.add_argument('name', type=str, required=True, help="Author name")
    parser.add_argument('portrait', type=str, help="Base64 encoded image string")
    parser.add_argument('portrait_filename', type=str, help="Image filename")

    author_book_fields = {
        'book_id': fields.Integer,
        'name': fields.String,
    }

    fields = {
        'author_id': fields.Integer,
        'name': fields.String,
        'portrait': fields.String,
        'books': fields.List(fields.Nested(author_book_fields))
    }


class AuthorListResource(BaseAuthorResource, PaginatedListResource):

    @jwt_required()
    def post(self):
        args = self.parser.parse_args()
        portrait_name, portrait = args['portrait_filename'], args['portrait']

        author = Author(args['name'])
        if portrait_name and portrait:
            author.portrait = decode_image(name=secure_filename(portrait_name), data64=portrait, max_length=255)
        author.save()

        return marshal(author, self.fields, envelope='book'), 200

    def get_query(self):
        # переделать в ретурн todo:
        query = super().get_query()
        return query.order_by(self.model.author_id.asc())


class AuthorResource(BaseAuthorResource, ObjectResource):
    model_id_field = 'author_id'
    arg_id = 'id'

    @jwt_required()
    def put(self, id):
        self.object_id = id
        self.get_object()

        args = self.parser.parse_args()
        portrait_name, portrait = args['portrait_filename'], args['portrait']

        author = self.object
        author.name = args['name']

        prev_portrait = author.portrait

        if portrait_name and portrait:
            author.portrait = decode_image(name=secure_filename(portrait_name), data64=portrait, max_length=255)
        author.save()

        if portrait_name and portrait and prev_portrait:
            os.remove(prev_portrait)
        return marshal(author, self.fields, envelope='book'), 200


class BaseBookResource:
    model = Book

    parser = reqparse.RequestParser()
    parser.add_argument('name', type=str, required=True, help="Book name")
    parser.add_argument('authors', type=int, action='append', default=[])
    parser.add_argument('cover_image', type=str, help="Base64 encoded image string")
    parser.add_argument('cover_image_filename', type=str, help="Image filename")

    book_author_fields = {
        'author_id': fields.Integer,
        'name': fields.String
    }

    fields = {
        'book_id': fields.Integer,
        'cover_image': fields.String,
        'name': fields.String,
        'authors': fields.List(fields.Nested(book_author_fields))
    }


class BookListResource(BaseBookResource, PaginatedListResource):

    @jwt_required()
    def get(self):
        print(current_user)
        return super().get()

    @jwt_required()
    def post(self):
        args = self.parser.parse_args()
        cover_image_name, cover_image = args.get('cover_image_filename'), args['cover_image']

        book = Book(args['name'], args["authors"])

        if cover_image_name and cover_image:
            book.cover_image = decode_image(name=secure_filename(cover_image_name), data64=cover_image, max_length=255)
        book.save()

        return marshal(book, self.fields, envelope='book'), 200


class BookResource(BaseBookResource, ObjectResource):
    model_id_field = 'book_id'
    arg_id = 'book_id'

    @jwt_required()
    def put(self, id):
        self.object_id = id
        self.get_object()

        args = self.parser.parse_args()
        cover_image_name, cover_image = args.get('cover_image_filename'), args['cover_image']

        book = self.object
        book.name = args['name']
        book.update_authors(args['authors'])
        prev_cover = book.cover_image

        if cover_image_name and cover_image:
            book.cover_image = decode_image(name=secure_filename(cover_image_name), data64=cover_image, max_length=255)
        book.save()

        if cover_image_name and cover_image and prev_cover:
            os.remove(prev_cover)

        return marshal(book, self.fields, envelope='book'), 200


class LoginResource(OnlyJsonMixin, Resource):

    def post(self):
        username = request.json.get("username", None)
        password = request.json.get("password", None)

        user = User.query.filter(User.username == username).one_or_none()

        if not user or not check_password_hash(user.password, password):
            return make_response(jsonify({"message": "Bad username or password"}), 401)

        access_token = create_access_token(identity=user)
        refresh_token = create_refresh_token(identity=user)

        user.refresh_token = get_jti(refresh_token)
        user.save()

        return jsonify(access_token=access_token, refresh_token=refresh_token)


class RefreshResource(Resource):
    @jwt_required(refresh=True)
    def post(self):
        if get_jwt().get('jti') == current_user.refresh_token:
            access_token = create_access_token(identity=current_user)
            return jsonify(access_token=access_token)
        else:
            return make_response(jsonify({"message": "Incorrect or expired token"}), 401)


def index():
    user = {'username': 'Murad'}
    apis = [
        {
            'address': url_for('book_list'),
            'name': 'Books'
        },
        {
            'address': url_for('author_list'),
            'name': 'Authors'
        },
    ]
    return render_template('index.html', title='Home', user=user, apis=apis)
