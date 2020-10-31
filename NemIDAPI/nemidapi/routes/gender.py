from flask import request, jsonify
# from __init__.py file import app - for routes (@app.route)
from nemidapi import app
import random
from datetime import datetime

@app.route('/gender', methods=['POST'])
def create_gender():
    label = request.json['label']
    
    try:
        # storing in DB will be here
        pass
    except Exception as e:
        # print(f"******* Error in routes/customers.py: add_customer() *******")
        print(f"Error: {e}")
        return jsonify("Server error: unable to register user. See console for more info."), 500
    else:
        return jsonify(f'{label}')
