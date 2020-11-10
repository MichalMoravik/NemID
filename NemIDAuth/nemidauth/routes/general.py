from flask import request, jsonify
from datetime import datetime
# from __init__.py file import app - for routes (@app.route)
from nemidauth import app
from nemidauth.dbconfig import get_db
import json
import requests

#/login - Receives a NemId and password, sends a call to the NemID API:
#If the auth request is successful add it to the database - State pending
#If the auth request failed - return an error (403 or something)
@app.route('/login', methods=['POST'])
def login():
    """Logs in the user by calling NemID API authentication route and passing the data inside.
    Receives the NemID number and password as request body elements.
    If successful (the user is authenticated), it will store the pending state in the DB.

    Returns:
        Various json strings and status codes based on different conditions. 
        These status codes and messages are returned from NemID API response. 
        
        If successful, the user's data in a form of json are returned.
    """
    try:
        nem_id = str(request.json['nemId'])
        password = str(request.json['password'])
    except Exception as e:
        print(f"*** Error in routes/general/login() *** \n{e}")
        return jsonify("Server error: Check JSON spelling!"), 500
    else:
        try:
            data = {
                'nemId': nem_id,
                'password': password
            }
            response = requests.post('http://127.0.0.1:5555/authenticate', json=data)
        except Exception as e:
            print(f"*** Error in routes/general/login() *** \n{e}")
            return jsonify("Server error: could not login!"), 500
        else:
            try:
                if response.ok:
                    # STORE IN DB
                    # cur = get_db().cursor()
                    # cur.execute('')
                    pass
            except Exception as e:
                # EXCEPT IF DB CONNECTION FAILS (only triggered if response is OK (200))
                pass
            else:
                # RETURN RESPONSE CODE (all possible response codes)
                # won't be returned if DB connection fails
                return jsonify (json.loads(response.content)), response.status_code
            

@app.route('/change-password', methods=['POST'])
def change_password():
    """Changes user's password by calling NemID API and passing the data. 
    Receives the NemID number, old password, and the new password as request body elements.

    Returns:
        Various json strings and status codes based on different conditions. 
        These status codes and messages are returned from NemID API response. 
    """
    try:
        nem_ID = str(request.json['nemId'])
        old_password = str(request.json['oldPassword'])
        new_password = str(request.json['newPassword'])
    except Exception as e:
        print(f"*** Error in routes/general/change_password() *** \n{e}")
        return jsonify("Server error: Check JSON spelling!"), 500
    else:
        try:
            data = {
                'nemId': nem_ID,
                'oldPassword': old_password,
                'newPassword': new_password
            }
            response = requests.post('http://127.0.0.1:5555/change-password', json=data)
        except Exception as e:
            print(f"*** Error in routes/general/change_password() *** \n{e}")
            return jsonify("Server error: could not change the password!"), 500
        else:
            return jsonify (json.loads(response.content)), response.status_code


@app.route('/reset-password', methods=['POST'])
def reset_password():
    """Resets user's password by calling NemID API and passing the data. 
    Receives the CPR number and password as request body elements.

    Returns:
        Various json strings and status codes based on different conditions. 
        These status codes and messages are returned from NemID API response. 
    """
    try:
        cpr = str(request.json['cpr'])
        password = str(request.json['password'])
    except Exception as e:
        print(f"*** Error in routes/general/reset_password() *** \n{e}")
        return jsonify("Server error: Check JSON spelling!"), 500
    else:
        try:
            data = {
                'cpr': cpr,
                'password': password
            }
            response = requests.post('http://127.0.0.1:5555/reset-password', json=data)
        except Exception as e:
            print(f"*** Error in routes/general/reset_password() *** \n{e}")
            return jsonify("Server error: could not reset the password!"), 500
        else:
            return jsonify (json.loads(response.content)), response.status_code