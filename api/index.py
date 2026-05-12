import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from serverless_wsgi import handle_request
from app import app, init_db

init_db()

def handler(event, context):
    return handle_request(app, event, context)