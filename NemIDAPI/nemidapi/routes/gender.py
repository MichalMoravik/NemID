from flask import request, jsonify
# from __init__.py file import app - for routes (@app.route)
from nemidapi import app
from nemidapi.models.user import *
from nemidapi.models.gender import *
import random
from datetime import datetime

@app.route('/gender', methods=['POST'])
def create_gender():
    try:
        label = request.json['label']
        
        new_gender = Gender(label)
        db.session.add(new_gender)
        db.session.commit()

        return jsonify(f'{label}')
    except Exception as e:
        # print(f"******* Error in routes/customers.py: add_customer() *******")
        print(f"Error: {e}")
        return jsonify("Server error: unable to register user. See console for more info."), 500

