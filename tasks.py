from celery import Celery
import os


CELERY_BROKER_URL = 'pyamqp://guest@localhost//',
CELERY_RESULT_BACKEND = 'pyamqp://guest@localhost//'

app = Celery('tasks', broker=CELERY_BROKER_URL)

@app.task
def add(x, y):
    print(os.path.dirname(os.path.realpath(__file__)))
    return x + y