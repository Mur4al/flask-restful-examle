import os

from flask import send_from_directory
from flask_restful import Api

from api import app
from api.controllers import index, BookListResource, AuthorListResource, BookResource, AuthorResource, LoginResource, \
    RefreshResource


app.add_url_rule('/', 'index', index)

api = Api(app)
api.add_resource(BookListResource, '/books', endpoint='book_list')
api.add_resource(BookResource, '/books/<int:id>', endpoint='book_object')
api.add_resource(AuthorListResource, '/authors', endpoint='author_list')
api.add_resource(AuthorResource, '/authors/<int:id>', endpoint='author_object')

api.add_resource(LoginResource, '/auth/login', endpoint='login')
api.add_resource(RefreshResource, '/auth/refresh', endpoint='refresh')



if app.config["DEBUG"]:
    app.add_url_rule('/media/<path:filename>', 'media',
                     lambda filename: send_from_directory(os.path.join(os.getcwd(), app.config["UPLOAD_FOLDER"]), filename))

