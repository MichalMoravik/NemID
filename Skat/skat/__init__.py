from flask import Flask
app = Flask(__name__)
from skat.routes import user, year, general