import os

bind = f"0.0.0.0:{os.getenv('API_PORT', '8001')}"
workers = 2
threads = 4
worker_class = "uvicorn.workers.UvicornWorker"

loglevel = "debug"
accesslog = "-"
errorlog = "-"
