FROM python:3.8

RUN mkdir /code

ENV PIP_NO_CACHE_DIR=off \
  PYTHONUNBUFFERED=1 \
  TZ=Europe/Moscow \
  FLASK_APP=api

WORKDIR /code
COPY . .

RUN pip install -U pip setuptools wheel
RUN pip install -U -r requirements.txt

RUN chmod +x "./entrypoint.sh"
ENTRYPOINT ["sh", "./entrypoint.sh"]

EXPOSE 80

CMD ["uwsgi", "./uwsgi.ini"]
