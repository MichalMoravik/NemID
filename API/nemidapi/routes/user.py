from flask import request, jsonify
from datetime import datetime
import random
# from __init__.py file import app - for routes (@app.route)
from nemidapi import app
from nemidapi.dbconfig import get_db
import json
import hashlib

# HELPERS
def generate_nem_ID_number(cpr: str):
    """will generate nemID number in form of: {random 5 digits}-{last four digits of CPR}

    Args:
        cpr (str): cpr in a string form

    Returns:
        str: nem id number
    """
    last_four_digits = cpr[-4:]
    random_five_digits = random.randint(10000, 99999)
    return f'{random_five_digits}-{last_four_digits}'


@app.route('/user', methods=['POST'])
def create_user():
    """Creates new user and stores it in the database.

    Returns:
        Various json strings and status codes based on different situations
    """
    try:
        email = str(request.json['email']).lower()
        cpr = str(request.json['cpr'])
        created_at = datetime.now().strftime("%B %d, %Y %I:%M%p")
        modified_at = datetime.now().strftime("%B %d, %Y %I:%M%p")
        gender_id = int(request.json['genderId'])
        nem_ID = generate_nem_ID_number(cpr) 
        password_hash = hashlib.sha256(str.encode(request.json['password'])).hexdigest()
    except Exception as e:
        print(f"*** Error in routes/user/create_user() ***: \n{e}")
        return jsonify("Check spelling and data types of request body elements!"), 400
    else:  
        try:
            cur = get_db().cursor()
            
            cur.execute(f"SELECT 1 FROM User WHERE CPR=?", (cpr,))
            record = cur.fetchone()
            if record is not None:
                return jsonify(f'User with CPR {cpr} already exists!'), 403
            
            # check if the assigned gender exists
            cur.execute(f"SELECT 1 FROM Gender WHERE Id=?", (gender_id,))
            record = cur.fetchone()
            if record is None:
                return jsonify(f'Gender with the gender ID: {gender_id} does not exist!'), 404
            
            # transaction - inserts user and password atomically
            # in password insertion, the UserId is found by looking 
            # at the last added and highest Id, which is always the new user.
            commands = [
                ('INSERT INTO User(Email, NemId, CPR, CreatedAt, ModifiedAt, GenderId) VALUES (?,?,?,?,?,?)', 
                            (email, nem_ID, cpr, created_at, modified_at, gender_id)),
                ('INSERT INTO Password(PasswordHash, UserId, CreatedAt, IsValid) ' \
                'SELECT ?, User.Id, ?, ? FROM User ORDER BY Id DESC LIMIT 1', 
                            (password_hash, created_at, 1))]
            for command in commands:
                    cur.execute(command[0], command[1])
            get_db().commit()
        except Exception as e:
            print(f"*** Error in routes/user/create_user() ***: \n{e}")
            return jsonify("Server error: unable to register user!"), 500
        else:
            return jsonify(f"User with CPR {cpr} was created!"), 201


@app.route('/user/<id>', methods=['PUT'])
def update_user(id):
    """Updates the user and stores the new data in the database

    Args:
        id: taken from the route URL e.g. ...user/1

    Returns:
        Various json strings and status codes based on different situations
    """
    try:
        email = str(request.json['email']).lower()
        cpr = str(request.json['cpr']).lower()
        modified_at = datetime.now().strftime("%B %d, %Y %I:%M%p")
        gender_id = int(request.json['genderId'])
        nem_ID = generate_nem_ID_number(cpr)
        id = int(id)       
    except Exception as e:
        print(f"*** Error in routes/user/update_user() ***: \n{e}")
        return jsonify("Check spelling and data types of request body elements!"), 400
    else:  
        try:
            cur = get_db().cursor()
            cur.execute('UPDATE User SET Email=?, CPR=?, ModifiedAt=?, GenderId=?, NemId=?  WHERE Id=?', 
                        (email, cpr, modified_at, gender_id, nem_ID, id, ))
        except Exception as e:
            print(f"*** Error in routes/user/update_user() ***: \n{e}")
            return jsonify("Server error: Cannot update user!"), 500
        else:
            if cur.rowcount == 1:
                try:
                    get_db().commit()
                except Exception as e:
                    print(f"*** Error in routes/user/update_user() ***: \n{e}")
                    return jsonify("Server error: Cannot update user!"), 500
                else:
                    return jsonify(f'User with id: {id} updated!'), 200
            return jsonify(f'User with id {id} does not exists!'), 404


@app.route('/user/<id>', methods=['DELETE'])
def delete_user(id):
    """Removes the user from the database

    Args:
        id: taken from the route URL e.g. ...user/1

    Returns:
        Various json strings and status codes based on different situations
    """
    try:
        id = int(id)     
    except Exception as e:
        print(f"*** Error in routes/user/delete_user() ***: \n{e}")
        return jsonify("This ID could not be parsed to integer!"), 422
    else:  
        try:
            cur = get_db().cursor()
            cur.execute("DELETE FROM User WHERE Id=?", (id,))
        except Exception as e:
            print(f"*** Error in routes/user/delete_user() ***: \n{e}")
            return jsonify("Server error: Cannot delete user!"), 500
        else:
            if cur.rowcount == 1:
                try:
                    get_db().commit()
                except Exception as e:
                    print(f"*** Error in routes/user/delete_user() ***: \n{e}")
                    return jsonify("Server error: Cannot delete user!"), 500
                else:
                    return jsonify(f'User with id: {id} deleted!'), 200
            return jsonify(f'User with id {id} does not exists!'), 404
    

@app.route('/user', methods=['GET'])
def get_users():
    """Pulls and returns all users from the database

    Returns:
        Various json strings and status codes based on different situations
        If successful, the users' data in a form of json are returned.
    """
    try:
        cur = get_db().cursor()
        cur.execute("SELECT * FROM User")
        rows = cur.fetchall()
    except Exception as e:
        print(f"*** Error in routes/user/get_users() ***: \n{e}")
        return jsonify("Server error: Cannot get users!"), 500
    else: 
        if rows:
            users = [dict(user) for user in rows]
            return json.dumps(users), 200
        return jsonify(f'There are no users in the database!'), 404


@app.route('/user/<id>', methods=['GET'])
def get_user(id):
    """Pull a specific user from the database

    Args:
        id: taken from the route URL e.g. ...user/1

    Returns:
        Various json strings and status codes based on different situations
        If successful, the user's data in a form of json are returned.
    """
    try:
        id = int(id)     
    except Exception as e:
        print(f"*** Error in routes/user/get_user() ***: \n{e}")
        return jsonify("This ID could not be parsed to integer!"), 422
    else:
        try:
            cur = get_db().cursor()
            cur.execute("SELECT * FROM User WHERE Id=?", (id,))
            row = cur.fetchone()
        except Exception as e:
            print(f"*** Error in routes/user/get_user() ***: \n{e}")
            return jsonify("Server error: Cannot get user!"), 500
        else:
            if row is None:
                return jsonify(f'User with id {id} does not exists'), 404
            user = dict(row)
            return json.dumps(user), 200



