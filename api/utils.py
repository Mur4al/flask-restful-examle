import base64
import datetime
import os

from flask_restful import abort
from api import app, jwt
from api.models import User


def generate_filename(name:str)->str:
    return f'{name}_{datetime.datetime.now().strftime("%y%m%d_%H%M%S%f")}'

def decode_image(name:str, data64:str, max_length:int)->str:

    upload_folder = app.config["UPLOAD_FOLDER"]
    if not is_image(name):
        abort(400, msg={'portrait_filename': 'Not an image'})
    filename, ext = os.path.splitext(name)

    trunc = max_length - len(upload_folder) - len(name)
    print(trunc)
    if trunc < 0:
        filename = filename[:trunc]

    filename=generate_filename(filename)
    path = os.path.join(upload_folder,f"{filename}{ext}")

    byte_data = base64.b64decode(data64)

    with open(path,'wb') as file:
        file.write(byte_data)
    return path

def is_image(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ['jpg','png','gif']


@jwt.user_lookup_loader
def jwt_user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.filter_by(user_id=identity).one_or_none()


@jwt.user_identity_loader
def jwt_user_identity_lookup(user):
    return user.user_id