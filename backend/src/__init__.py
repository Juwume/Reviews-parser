from flask import Flask

app = Flask(__name__)
# src.config.from_object(os.environ.get('FLASK_ENV') or 'config.DevelopementConfig')


from src.views import *
