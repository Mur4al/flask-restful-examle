from flask import Flask
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

from .cli import create_superuser
from .models import db
import settings

app = Flask(__name__)

app.config.from_object(settings.Settings)
app.url_map.strict_slashes = False

db.app = app
db.init_app(app)

migrate = Migrate(app, db)

jwt = JWTManager(app)

app.cli.add_command(create_superuser)

from api import routes
