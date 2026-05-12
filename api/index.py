import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from serverless_wsgi import handle_request_wsgi
from app import app

def handler(event, context):
    return handle_request_wsgi(app, event, context)