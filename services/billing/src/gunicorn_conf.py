import os

bind = f"0.0.0.0:{os.getenv('APP_PORT', "8071")}"
workers = 2
threads = 4
worker_class = "uvicorn.workers.UvicornWorker"

loglevel = "debug"
accesslog = "-"
errorlog = "-"
