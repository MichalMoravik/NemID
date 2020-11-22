from flask import Flask
app = Flask(__name__)
from nemidbank.routes import bankuser, account, general




