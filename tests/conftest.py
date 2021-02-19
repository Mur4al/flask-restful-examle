import logging
import os
import tempfile

import alembic
import pytest
from flask_migrate import upgrade

from api import app


@pytest.fixture(scope='class', autouse=True)
def client():
    #setup
    db_fd, db_location = tempfile.mkstemp()
    app.config['SQLALCHEMY_DATABASE_URI']=f'sqlite:///{db_location}'
    app.config['TESTING'] = True

    #убираем вывод миграций
    logging.disable(logging.WARNING)

    app_context = app.test_request_context()
    with app.test_client() as client:
        with app_context:
            upgrade()
        yield client
    #teardown
    os.close(db_fd)
    os.unlink(db_location)