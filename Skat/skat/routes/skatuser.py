from flask import request, jsonify
from datetime import datetime
from skat import app
from skat.dbconfig import get_db
import json

@app.route('/skatuser', methods=['POST'])
def create_skat_user():
    """Adds a new user to the skat system. 
    Stores by the user id taken from the request body.

    Returns:
        Various json strings and status codes based on different conditions.
        If successful, creates the skat user and returns the success message with 201 status code.
    """
    try:
        user_id = int(request.json['userId'])
    except Exception as e:
        print(f"*** Error in routes/skatuser/create_skat_user() ***: \n{e}")
        return jsonify("Check spelling and data types of request body elements!"), 400 
    else:
        try:
            cur = get_db().cursor()
            
            cur.execute(f"SELECT 1 FROM SkatUser WHERE UserId=?", (user_id,))
            record = cur.fetchone()
            if record is not None:
                return jsonify(f'User with id: {user_id} is already registered in the system!'), 200
            
            current_datetime = datetime.now().strftime("%B %d, %Y %I:%M%p")
            
            cur.execute('INSERT INTO SkatUser(UserId, CreatedAt, IsActive) VALUES (?,?,?)', 
                        (user_id, current_datetime, 1))
            get_db().commit()
        except Exception as e:
            print(f"*** Error in routes/skatuser/create_skat_user() ***: \n{e}")
            return jsonify("Server error: unable to register a new skat user!"), 500
        else:
            return jsonify(f"A new skat user with user id: {user_id} was successfully registered!"), 201


@app.route('/skatuser/<id>', methods=['PUT'])
def update_skat_user(id):
    """Updates the skat user with the specified id.

    Args:
        id (int): skat user ID taken from the route URL e.g. skatuser/1

    Returns:
        Various json strings and status codes based on different conditions.
        If successful, updates the skat user and returns the success message and 200 status code.
    """
    try:
        id = int(id)
        user_id = int(request.json['userId'])
        is_active = int(request.json['isActive'])
    except Exception as e:
        print(f"*** Error in routes/skatuser/update_skat_user() ***: \n{e}")
        return jsonify("Check spelling and data types of request body elements!"), 400 
    else:
        try:
            cur = get_db().cursor()            
            cur.execute('UPDATE SkatUser SET UserId=?, IsActive=? WHERE Id=?', 
                        (user_id, is_active, id, ))
        except Exception as e:
            print(f"*** Error in routes/skatuser/update_skat_user() ***: \n{e}")
            return jsonify("Server error: Cannot update the skat user!"), 500
        else:
            if cur.rowcount == 1:
                try:
                    get_db().commit()
                except Exception as e:
                    print(f"*** Error in routes/skatuser/update_skat_user() ***: \n{e}")
                    return jsonify("Server error: Cannot update the skat user!"), 500
                else:
                    return jsonify(f'A skat user with id: {id} was updated!'), 200
            return jsonify(f'A skat user with id: {id} does not exist!'), 404


@app.route('/skatuser/<id>', methods=['DELETE'])
def delete_skat_user(id):
    """Deletes the skat user with the specified id.

    Args:
        id (int): skat user ID taken from the route URL e.g. skatuser/1

    Returns:
        Various json strings and status codes based on different conditions.
        If successful, deletes the skat user and returns the success message and 200 status code.
    """
    try:
        id = int(id)     
    except Exception as e:
        print(f"*** Error in routes/skatuser/delete_skat_user() ***: \n{e}")
        return jsonify("Specified ID could not be parsed to integer!"), 422
    else:  
        try:
            cur = get_db().cursor()
            cur.execute("DELETE FROM SkatUser WHERE Id=?", (id,))
        except Exception as e:
            print(f"*** Error in routes/skatuser/delete_skat_user() ***: \n{e}")
            return jsonify("Server error: Cannot delete the skat user!"), 500
        else:
            if cur.rowcount == 1:
                try:
                    get_db().commit()
                except Exception as e:
                    print(f"*** Error in routes/skatuser/delete_skat_user() ***: \n{e}")
                    return jsonify("Server error: Cannot delete the skat user!"), 500
                else:
                    return jsonify(f'Skat user with id: {id} deleted!'), 200
            return jsonify(f'Skat user with id {id} does not exist!'), 404


@app.route('/skatuser/<id>', methods=['GET'])
def get_skat_user(id):    
    """Retrieves the skat user with the specified id from the database.

    Args:
        id (int): skat user ID taken from the route URL e.g. skatuser/1

    Returns:
        Various json strings and status codes based on different conditions.
        If successful, returns the skat user (JSON) and 200 status code.
    """
    try:
        id = int(id)     
    except Exception as e:
        print(f"*** Error in routes/user/get_skat_user() ***: \n{e}")
        return jsonify("Specified ID could not be parsed to integer!"), 422
    else:
        try:
            cur = get_db().cursor()
            cur.execute("SELECT * FROM SkatUser WHERE Id=?", (id,))
            row = cur.fetchone()
        except Exception as e:
            print(f"*** Error in routes/user/get_skat_user() ***: \n{e}")
            return jsonify("Server error: Cannot get user!"), 500
        else:
            if row is None:
                return jsonify(f'Skat user with id {id} does not exist'), 404
            user = dict(row)
            return json.dumps(user), 200
        

@app.route('/skatuser', methods=['GET'])
def get_skat_users():
    """Retrieves all skat users from the database.

    Returns:
        Various json strings and status codes based on different conditions.
        If successful, returns all the skat users (JSON) and 200 status code.
    """
    try:
        cur = get_db().cursor()
        cur.execute("SELECT * FROM SkatUser")
        rows = cur.fetchall()
    except Exception as e:
        print(f"*** Error in routes/user/get_skat_users() ***: \n{e}")
        return jsonify("Server error: Cannot get users!"), 500
    else: 
        if rows:
            users = [dict(user) for user in rows]
            return json.dumps(users), 200
        return jsonify(f'There are no skat users in the database!'), 404