from flask import request, jsonify
from datetime import datetime
from nemidskat import app
from nemidskat.dbconfig import get_db
import json
import requests