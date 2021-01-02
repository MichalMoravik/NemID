from flask import Flask
app = Flask(__name__)
from auth.routes import general 