from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from os import path

app = Flask(__name__)

basedir = path.abspath(path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    path.join(basedir, 'nemid.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

try:
    db = SQLAlchemy(app)
    ma = Marshmallow(app)
except Exception as e:
    print(f"******* Error in __init__.py: Cannot establish SQL connection *******")
    print(e)
    
# by importing routes after the app is initialized, circular import error are avoided
from nemidapi.routes import user, gender



