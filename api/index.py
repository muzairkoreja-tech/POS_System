import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, init_db

init_db()

def handler(event, context):
    path = event.get('path', '/') or '/'
    method = event.get('httpMethod', 'GET')
    headers = event.get('headers', {}) or {}
    query = event.get('queryStringParameters', {}) or {}
    
    environ = {
        'REQUEST_METHOD': method,
        'SCRIPT_NAME': '',
        'PATH_INFO': path,
        'QUERY_STRING': '&'.join(f'{k}={v}' for k, v in query.items()) if query else '',
        'SERVER_NAME': 'localhost',
        'SERVER_PORT': '80',
        'SERVER_PROTOCOL': 'HTTP/1.1',
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'https',
        'wsgi.input': event.get('body', '') or '',
        'wsgi.errors': sys.stderr,
        'wsgi.multithread': False,
        'wsgi.multiprocess': True,
        'wsgi.run_once': False,
    }
    
    for key, value in headers.items():
        environ[f'HTTP_{key.upper().replace("-", "_")}'] = value
    
    if 'content-type' in headers:
        environ['CONTENT_TYPE'] = headers['content-type']
    if 'content-length' in headers:
        environ['CONTENT_LENGTH'] = headers['content-length']
    
    response_started = {}
    response_headers = {}
    
    def start_response(status, headers):
        response_started['status'] = int(status.split()[0])
        response_headers.update(dict(headers))
    
    result = []
    app_iter = app(environ, start_response)
    for item in app_iter:
        if isinstance(item, bytes):
            result.append(item)
        else:
            result.append(item.encode() if isinstance(item, str) else item)
    
    body = b''.join(result)
    
    return {
        'statusCode': response_started.get('status', 200),
        'headers': response_headers,
        'body': body.decode('utf-8') if body else ''
    }