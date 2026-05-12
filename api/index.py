import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, init_db

init_db()

# For WSGI servers like Gunicorn
if __name__ != '__main__':
    application = app

if __name__ == '__main__':
    print("Starting POS server on http://localhost:5000")
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))