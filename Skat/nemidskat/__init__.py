from flask import Flask
app = Flask(__name__)
from nemidskat.routes import skatuser, skatyear, general