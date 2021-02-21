##Flask-restful example

Example flask-restful+sqlalchemy application in Docker.

Install [Docker](https://docs.docker.com/engine/install/) and [docker-compose](https://docs.docker.com/compose/install/)

Build application
```bash
docker-compose build
```

Apply alembic migrations

```bash
docker-compose run --rm web flask db upgrade
```

Run application

```bash
docker-compose up
```
The server will run on localhost:8000

To create a user.
```bash
docker-compose run --rm web flask create-superuser
```

