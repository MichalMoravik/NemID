from flask import Flask
app = Flask(__name__)
from borger.routes import user, address