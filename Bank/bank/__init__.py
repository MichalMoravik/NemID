from flask import Flask
app = Flask(__name__)
from bank.routes import user, account, general




