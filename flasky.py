from app import create_app

import os

app = create_app(os.getenv('FLASK_CONFIG') or 'default')



