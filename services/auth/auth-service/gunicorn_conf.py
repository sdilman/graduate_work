import os

bind = f"0.0.0.0:{os.getenv('API_PORT', '8001')}"
workers = 1
threads = 1
worker_class = "uvicorn.workers.UvicornWorker"
