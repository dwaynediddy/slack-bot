from celery import Celery

app = Celery('app', broker='http://127.0.0.1:5000/')
