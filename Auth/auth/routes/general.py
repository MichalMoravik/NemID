from flask import request, jsonify
from datetime import datetime
# from __init__.py file import app - for routes (@app.route)
from auth import app
from auth.dbconfig import get_db
import json
import requests
import random

# HELPERS
def generate_and_store_token(cursor, auth_attempt_id, nem_id):
    """Sending request to azure serverless function 'tokengenerator'.
    If the request is successful and token is generated, then a new Token is added to the Token table
    and StateId in AuthAttemp is updated to 2 (successful). If the token generation process fails, then
    StateId in AuthAttemp is updated to 3 (failed).

    Args:
        cursor (sqlite3 cursor): Cursor from database connection
        auth_attempt_id (int): Id of the record inside of AuthAttempt table
        nem_id (int): nemID number taken from the request when logging in

    Returns:
        Various json strings and status codes based on different situations
        If successful, then the function proceeds and does not return anything.
    """
    try:
        # send nemID and the nemID code to the tokengenerator serverless function
        response = requests.post('http://functions:80/api/tokengenerator', json={ "nemId": nem_id })
        
        # if the request to tokengenerator went okay and returned 200,
        # then store generated token in the token table
        # and change StateId of AuthAttempt table
        if response.ok:
            # returned generated token
            generated_token = json.loads(response.content)['token']
            
            # current datetime
            created_at = datetime.now().strftime("%B %d, %Y %I:%M%p")
            
            # transaction - store in token table and change StateId in AuthAttempt to successful (id 2)
            commands = [
                ('INSERT INTO Token(AuthAttemptId, Token, CreatedAt) VALUES (?,?,?)',
                (auth_attempt_id, generated_token, created_at)),
                ('UPDATE AuthAttempt SET StateId=? WHERE Id=?', (2, auth_attempt_id))
            ]
            for command in commands:
                cursor.execute(command[0], command[1])
        else:
            # change StateId of AuthAttempt to failed (id 3)
            cursor.execute('UPDATE AuthAttempt SET StateId=? WHERE Id=?', (3, auth_attempt_id))
            return jsonify("Server error in routes/general/login(): Could not generate JWT token!"), 500
    except Exception as e:
        # change StateId of AuthAttempt to failed (id 3)
        cursor.execute('UPDATE AuthAttempt SET StateId=? WHERE Id=?', (3, auth_attempt_id))
        print(f"*** Error in routes/general/login() *** \n{e}")
        return jsonify("Server error: Could not receive the response" \
            "from the 'tokengenerator' serverless function!"), 500
    

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
        return jsonify("Check spelling and data types of request body elements!"), 400
    else:
        try:
            data = {
                'nemId': nem_id,
                'password': password
            }
            response = requests.post('http://nemid:83/authenticate', json=data)
        except Exception as e:
            print(f"*** Error in routes/general/login() *** \n{e}")
            return jsonify("Server error: could not login!"), 500
        else:
            try:
                # if the authentication went successful, 
                # then store state and auth attempt in the DB
                if response.ok:
                    cur = get_db().cursor()
                    
                    # generate nemID auth code
                    generated_code = str(random.randint(100000, 999999))
                    # current datetime
                    created_at = datetime.now().strftime("%B %d, %Y %I:%M%p")
                    
                    # insert a new auth attempt with pending state (stateId 1) to DB
                    cur.execute('INSERT INTO AuthAttempt(NemId, GeneratedCode, CreatedAt, StateId) VALUES (?,?,?,?)',
                        (nem_id, generated_code, created_at, 1))
                    # getting id of the inserted row
                    auth_attempt_id = cur.lastrowid
                    
                    generate_and_store_token(cur, auth_attempt_id, nem_id)
                        
                    # if everything went without problems, commit to DB
                    get_db().commit()
            except Exception as e:
                # except if database commands failed. The database queries can only be triggered 
                # if response is "ok" and so this exception is associated with database connection. 
                # Check the database connection, tables, and rules.
                print(f"*** Error in routes/general/login() *** \n{e}")
                print("User was successfully returned but insertion of data in database failed!")
                return jsonify("Server error: could not login because of database failure!"), 500
            else:
                return jsonify(json.loads(response.content)), response.status_code
            

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
        return jsonify("Check spelling and data types of request body elements!"), 400
    else:
        try:
            data = {
                'nemId': nem_ID,
                'oldPassword': old_password,
                'newPassword': new_password
            }
            response = requests.post('http://nemid:83/change-password', json=data)
        except Exception as e:
            print(f"*** Error in routes/general/change_password() *** \n{e}")
            return jsonify("Server error: could not change the password!"), 500
        else:
            return jsonify(json.loads(response.content)), response.status_code


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
        return jsonify("Check spelling and data types of request body elements!"), 400
    else:
        try:
            data = {
                'cpr': cpr,
                'password': password
            }
            response = requests.post('http://nemid:83/reset-password', json=data)
        except Exception as e:
            print(f"*** Error in routes/general/reset_password() *** \n{e}")
            return jsonify("Server error: could not reset the password!"), 500
        else:
            return jsonify(json.loads(response.content)), response.status_code