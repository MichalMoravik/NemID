from flask import Flask
app = Flask(__name__)
from nemidborger.routes import user, address