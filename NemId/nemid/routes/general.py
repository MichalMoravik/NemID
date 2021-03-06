from flask import request, jsonify
from datetime import datetime
# from __init__.py file import app - for routes (@app.route)
from nemid import app
from nemid.dbconfig import get_db
import json
import hashlib
import nemid.validations.requestdata as val


@app.route('/reset-password', methods=['POST'])
def reset_password():
    """Resets password. Receives CPR and Password from the request body. 
    Deactivates the old password for a user, and creates and stores the new password.

    Returns:
        Various json strings and status codes based on different situations.
        If successful, returns success message and 201 status code.
    """
    try:
        cpr = val.empty_validation(str(request.json['cpr']))
        password_hash = hashlib.sha256(val.empty_validation(str.encode(request.json['password']))).hexdigest()
    except Exception as e:
        print(f"*** Error in routes/general/reset_password() *** \n{e}")
        return jsonify("Check spelling and data types of request body elements!"), 400
    else:
        try:
            cur = get_db().cursor()
            
            # select user based on the CPR number and check if exists
            cur.execute("SELECT Id FROM User WHERE CPR=?", (cpr,))
            selected_user = cur.fetchone()
            if selected_user is None:
                return jsonify(f'User with this CPR: {cpr} does not exist!'), 404
            selected_user_id = dict(selected_user)["Id"]
                
            try:
                # current day and time
                created_at = datetime.now().strftime("%B %d, %Y %I:%M%p")

                # transaction - set IsValid to 0 (false) for the old and active password. 
                # then stores and activates a new hashed password
                commands = [
                    ('UPDATE Password SET IsValid=? WHERE UserId=? AND IsValid=?', (0, selected_user_id, 1)),
                    ('INSERT INTO Password(PasswordHash, UserId, CreatedAt, IsValid) VALUES (?,?,?,?)',
                    (password_hash, selected_user_id, created_at, 1))]
                for command in commands:
                    cur.execute(command[0], command[1])
                get_db().commit()
            except Exception as e:
                print(f"*** Error in routes/general/reset_password() *** \n{e}")
                return jsonify("Server error: could not store the new password!"), 500
        except Exception as e:
            print(f"*** Error in routes/general/reset_password() *** \n{e}")
            return jsonify("Server error: could not reset the password!"), 500
        else:
            return jsonify("The new password was stored and activated!"), 201


@app.route('/change-password', methods=['POST'])
def change_password():
    """Changes password from the old hashed password to the new hashed password.  
    Receives NemID number, old password (for validation), and new password from the request body.

    Returns:
        Various json strings and status codes based on different situations.
        If successful, returns success message and 201 status code.
    """
    try:
        nem_ID = str(request.json['nemId'])
        old_password_hash = hashlib.sha256(val.empty_validation(str.encode(request.json['oldPassword']))).hexdigest()
        new_password_hash = hashlib.sha256(val.empty_validation(str.encode(request.json['newPassword']))).hexdigest()
    except Exception as e:
        print(f"*** Error in routes/general/change_password() *** \n{e}")
        return jsonify("Check spelling and data types of request body elements!"), 400
    else:
        try:
            cur = get_db().cursor()
            
            # select user based on NemID and check if exists
            cur.execute("SELECT Id FROM User WHERE NemId=?", (nem_ID,))
            selected_user = cur.fetchone()
            
            if selected_user is None:
                return jsonify(f'User with this NemID: {nem_ID} does not exist!'), 404
            selected_user_id = dict(selected_user)["Id"]
            
            # check if user's old password matches with the old password taken from the request body
            cur.execute("SELECT PasswordHash FROM Password WHERE UserId=? AND IsValid=?", (selected_user_id,1))
            selected_password = cur.fetchone()
            
            if selected_password is None:
                return jsonify(f'User with this NemID: {nem_ID} does not have any active password!'), 404
            selected_password_hash = dict(selected_password)["PasswordHash"]
            
            if selected_password_hash != old_password_hash.strip():
                return jsonify(f'The old password is not correct!'), 401
            
            try:
                # current day and time
                created_at = datetime.now().strftime("%B %d, %Y %I:%M%p")
                
                # Transaction - set IsValid to 0 (false) for the old and active password. 
                # Inserts the newly created password to the database.
                commands = [
                    ('UPDATE Password SET IsValid=? WHERE UserId=? AND IsValid=?', (0, selected_user_id, 1)),
                    ('INSERT INTO Password(PasswordHash, UserId, CreatedAt, IsValid) VALUES (?,?,?,?)',
                    (new_password_hash, selected_user_id, created_at, 1))]
                
                for command in commands:
                    cur.execute(command[0], command[1])
                    
                get_db().commit()
            except Exception as e:
                print(f"*** Error in routes/general/change_password() *** \n{e}")
                return jsonify("Server error: could not store the new password!"), 500
        except Exception as e:
            print(f"*** Error in routes/general/change_password() *** \n{e}")
            return jsonify("Server error: could not change the password!"), 500
        else:
            return jsonify("The new password was stored and activated!"), 201


@app.route('/authenticate', methods=['POST'])
def authenticate():
    """Authenticate if the user's credentials are valid. 
    Receives the NemID number and current hashed password. 

    Returns:
        Various json strings and status codes based on different situations
        If successful, the user's data in a form of JSON are returned.
    """
    try:
        password = hashlib.sha256(val.empty_validation(str.encode(request.json['password']))).hexdigest()
        nem_ID = request.json['nemId']
    except Exception as e:
        print(f"*** Error in routes/general/authenticate() *** \n{e}")
        return jsonify("Check spelling and data types of request body elements!"), 400
    else:
        try:
            cur = get_db().cursor()
            
            # select user based on NemID and check if exists 
            cur.execute("SELECT * FROM User WHERE NemId=?", (nem_ID,))
            selected_user = cur.fetchone()
            if selected_user is None:
                return jsonify(f'User with this NemID: {nem_ID} does not exist!'), 404
            selected_user = dict(selected_user)
            
            # selects current hashed password in the database
            # checks if the password exists
            cur.execute("SELECT PasswordHash FROM Password WHERE UserId=? AND IsValid=?", (selected_user['Id'], 1))
            selected_password = cur.fetchone()
            if selected_password is None:
                return jsonify(f'Password for the user with NemID: {nem_ID} does not exist!'), 404
            selected_password_hash = dict(selected_password)['PasswordHash']
            
        except Exception as e:
            print(f"*** Error in routes/general/authenticate() *** \n{e}")
            return jsonify("Server error: unable to authenticate!"), 500
        else:
            # checks if the hashed password from the database 
            # is exactly same as the one passed to the request body
            if password == selected_password_hash: 
                return json.dumps(selected_user), 200
            else:
                return jsonify("Incorrect password!"), 401