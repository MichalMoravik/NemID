from flask import Flask
app = Flask(__name__)
from nemidapi.routes import user, gender, general




