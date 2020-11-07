from flask import request, jsonify
from datetime import datetime
# from __init__.py file import app - for routes (@app.route)
from nemidapi import app
from nemidapi.dbconfig import get_db
import json
import hashlib

#reset-password - Receives a CPR and Password -¿ Deactivates all the other passwords for a user and creates a new password
@app.route('/reset-password', methods=['POST'])
def reset_password():
    try:
        cpr = str(request.json['cpr'])
        password = hashlib.sha256(str.encode(request.json['password'])).hexdigest()
        created_at = datetime.now().strftime("%B %d, %Y %I:%M%p")
    except Exception as e:
        print(f"************** Error **************: \n{e}")
        return jsonify("Server error: Check JSON spelling or conversion/hashing!"), 500
    else:
        try:
            cur = get_db().cursor()
            
            # select user based on CPR
            cur.execute("SELECT Id FROM User WHERE CPR=?", (cpr,))
            selected_user = cur.fetchone()
            if selected_user is None:
                return jsonify(f'User with this CPR: {cpr} does not exist!'), 404
            selected_user_id = dict(selected_user)["Id"]
                
            try:
                commands = [
                    ('UPDATE Password SET IsValid=? WHERE UserId=? AND IsValid=?', (0, selected_user_id, 1)),
                    ('INSERT INTO Password(PasswordHash, UserId, CreatedAt, IsValid) VALUES (?,?,?,?)',
                    (password, selected_user_id, created_at, 1))]
                for command in commands:
                    cur.execute(command[0], command[1])
                get_db().commit()
            except Exception as e:
                print(f"************** Error while updating/inserting a new password **************: \n{e}")
                return jsonify("Server error: could not store the new password!"), 500
        except Exception as e:
            print(f"************** Error while communicating with DB **************: \n{e}")
            return jsonify("Server error: could not reset the password!"), 500
        else:
            return jsonify("The new password was stored and activated!"), 201

# /change-password - Receives a NemId, OldPassword, NewPassword -¿ Deactivates the old password and creates a new one
@app.route('/change-password', methods=['POST'])
def change_password():
    try:
        nem_ID = str(request.json['nemId'])
        old_password_hash = hashlib.sha256(str.encode(request.json['oldPassword'])).hexdigest()
        new_password_hash = hashlib.sha256(str.encode(request.json['newPassword'])).hexdigest()
        created_at = datetime.now().strftime("%B %d, %Y %I:%M%p")
    except Exception as e:
        print(f"************** Error **************: \n{e}")
        return jsonify("Server error: Check JSON spelling or conversion/hashing!"), 500
    else:
        try:
            cur = get_db().cursor()
            
            # select user based on nemID
            cur.execute("SELECT Id FROM User WHERE NemId=?", (nem_ID,))
            selected_user = cur.fetchone()
            if selected_user is None:
                return jsonify(f'User with this NemID: {nem_ID} does not exist!'), 404
            selected_user_id = dict(selected_user)["Id"]
            
            # check if user's old password matches with old password taken from the request body
            cur.execute("SELECT PasswordHash FROM Password WHERE UserId=? AND IsValid=?", (selected_user_id,1))
            selected_password = cur.fetchone()
            if selected_password is None:
                return jsonify(f'User with this NemID: {nem_ID} does not have any active password!'), 404
            selected_password_hash = dict(selected_password)["PasswordHash"]
            if selected_password_hash != old_password_hash.strip():
                return jsonify(f'The old password is not correct!'), 403
            
            try:
                commands = [
                    ('UPDATE Password SET IsValid=? WHERE UserId=? AND IsValid=?', (0, selected_user_id, 1)),
                    ('INSERT INTO Password(PasswordHash, UserId, CreatedAt, IsValid) VALUES (?,?,?,?)',
                    (new_password_hash, selected_user_id, created_at, 1))]
                for command in commands:
                    cur.execute(command[0], command[1])
                get_db().commit()
            except Exception as e:
                print(f"************** Error while updating/inserting a new password **************: \n{e}")
                return jsonify("Server error: could not store the new password!"), 500
        except Exception as e:
            print(f"************** Error while communicating with DB **************: \n{e}")
            return jsonify("Server error: could not change the password!"), 500
        else:
            return jsonify("The new password was stored and activated!"), 201


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
            
            cur.execute("SELECT PasswordHash FROM Password WHERE UserId=? AND IsValid=?", (selected_user['Id'],1))
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