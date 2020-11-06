from flask import request, jsonify
from datetime import datetime
import random
# from __init__.py file import app - for routes (@app.route)
from nemidapi import app
from nemidapi.dbconfig import get_db
import json
import hashlib


# When receiving POST request, create nemId for the user
# @app.route('/generate-nemId', methods=['POST'])
# def generate_nemId():
#     try:
#         cpr = request.json['cpr']
#         nemId = generate_nem_ID_number(cpr)
#         return jsonify({"nemId": nemId}), 201

#     except Exception as e:
#         print(f"******* Error in {script_name} when generating nemId *******")
#         print(f"Error: {e}")
#         return jsonify({"server error": "cannot generate nemID"}), 500

    
    
# Receives a NemId and password, returns the user if successful, error otherwise
@app.route('/authenticate', methods=['POST'])
def authenticate():
    try:
        password = hashlib.sha256(str.encode(request.json['password'])).hexdigest()
        nem_ID = request.json['nemId']
    except Exception as e:
        print(f"************** Error **************: \n{e}")
        return jsonify("Server error: Check JSON spelling!"), 500
    else:
        try:
            cur = get_db().cursor()
            cur.execute("SELECT * FROM User WHERE NemId=?", (nem_ID,))
            selected_user = cur.fetchone()
            if selected_user is None:
                return jsonify(f'User with this NemID: {nem_ID} does not exist!'), 404
            selected_user = dict(selected_user)
            
            cur.execute("SELECT PasswordHash FROM Password WHERE UserId=?", (selected_user['Id'],))
            selected_password = cur.fetchone()
            if selected_password is None:
                return jsonify(f'Password for the user with NemID: {nem_ID} does not exist!'), 404
            selected_password_hash = dict(selected_password)['PasswordHash']

        except Exception as e:
            print(f"************** Error **************: \n{e}")
            return jsonify("Server error: unable to authenticate!"), 500
        else:
            if password == selected_password_hash: 
                return json.dumps(selected_user), 200
            else:
                return jsonify("Incorrect password!"), 403
        