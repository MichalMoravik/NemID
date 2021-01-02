from flask import request, jsonify
from datetime import datetime
# from __init__.py file import app - for routes (@app.route)
from borger import app
from borger.dbconfig import get_db
import json


@app.route('/user', methods=['POST'])
def create_user():
    """Creates a new borger user, and adds the user to the database.

    Returns:
        Various json strings and status codes based on different conditions.
        If successful, the request returns a success message and 201 status code
    """
    try:
        user_id = int(request.json['userId'])
    except Exception as e:
        print(f"*** Error in routes/user/create_user() ***: \n{e}")
        return jsonify("Check spelling and data types of request body elements!"), 400 
    else:
        try:
            cur = get_db().cursor()
            
            cur.execute(f"SELECT 1 FROM BorgerUser WHERE UserId=?", (user_id,))
            record = cur.fetchone()
            if record is not None:
                return jsonify(f'User with id: {user_id} is already registered in the borger system!'), 200
            
            current_datetime = datetime.now().strftime("%B %d, %Y %I:%M%p")
            
            cur.execute('INSERT INTO BorgerUser(UserId, CreatedAt) VALUES (?,?)', 
                        (user_id, current_datetime))
            get_db().commit()
        except Exception as e:
            print(f"*** Error in routes/user/create_user() ***: \n{e}")
            return jsonify("Server error: unable to register a new borger user!"), 500
        else:
            return jsonify(f"A new borger user with user id: {user_id} has been successfully registered!"), 201
        
    
@app.route('/user/<id>', methods=['DELETE'])
def delete_user(id):
    """Deletes a borger user with specified id.

    Args:
        id: taken from the route URL e.g. user/1

    Returns:
        Various json strings and status codes based on different conditions.
        If successful, the request returns a success message and 200 status code
    """
    try:
        id = int(id)
    except Exception as e:
        print(f"*** Error in routes/user/delete_user() ***: \n{e}")
        return jsonify("Specified ID could not be parsed to integer!"), 422
    else:
        try:
            cur = get_db().cursor()
            cur.execute("DELETE FROM BorgerUser WHERE Id=?", (id,))
            
            if cur.rowcount == 1:
                get_db().commit()
                return jsonify(f'Borger user with id: {id} deleted!'), 200
            return jsonify(f'Borger user with id {id} does not exist!'), 404
            
        except Exception as e:
            print(f"*** Error in routes/user/delete_user() ***: \n{e}")
            return jsonify("Server error: Cannot delete the borger user!"), 500            


@app.route('/user/<id>', methods=['PUT'])
def update_user(id):
    """Updates a borger user with the specified id.

    Args:
        id: taken from the route URL e.g. user/1

    Returns:
        Various json strings and status codes based on different conditions.
        If successful, the request returns a success message and 200 status code
    """
    try:
        id = int(id)
        user_id = int(request.json['userId'])
    except Exception as e:
        print(f"*** Error in routes/user/update_user() ***: \n{e}")
        return jsonify("Check spelling and data types of request body elements!"), 400 
    else:
        try:
            cur = get_db().cursor()
            cur.execute('UPDATE BorgerUser SET UserId=? WHERE Id=?',(user_id, id))
            
            if cur.rowcount == 1:
                get_db().commit()
                return jsonify(f'A borger user with id: {id} was updated!'), 200
            return jsonify(f'A borger user with id: {id} does not exist!'), 404

        except Exception as e:
            print(f"*** Error in routes/user/update_user() ***: \n{e}")
            return jsonify("Server error: Cannot update the borger user!"), 500


@app.route('/user/<id>', methods=['GET'])
def get_user(id):
    """Retrieves a borger user with the specified id.

    Args:
        id: taken from the route URL e.g. user/1

    Returns:
        Various json strings and status codes based on different conditions.
        If successful, the request returns the borger user (JSON) and 200 status code
    """
    try:
        id = int(id)
    except Exception as e:
        print(f"*** Error in routes/user/get_user() ***: \n{e}")
        return jsonify("Specified ID could not be parsed to integer!"), 422
    else:  
        try:
            cur = get_db().cursor()
            cur.execute("SELECT * FROM BorgerUser WHERE Id=?", (id,))
            row = cur.fetchone()
        except Exception as e:
            print(f"*** Error in routes/user/get_user() ***: \n{e}")
            return jsonify("Server error: Cannot get the borger user!"), 500
        else:
            if row is None:
                return jsonify(f'Borger user with id {id} does not exist'), 404
            user = dict(row)
            return json.dumps(user), 200
    
    
@app.route('/user', methods=['GET'])
def get_users():
    """Retrieves all borger users from the database.

    Returns:
        Various json strings and status codes based on different conditions.
        If successful, returns all borger users (JSON) and 200 status code.
    """
    try:
        cur = get_db().cursor()
        cur.execute("SELECT * FROM BorgerUser")
        rows = cur.fetchall()
    except Exception as e:
        print(f"*** Error in routes/user/get_users() ***: \n{e}")
        return jsonify("Server error: Cannot get bank borger users!"), 500
    else: 
        if rows:
            users = [dict(user) for user in rows]
            return json.dumps(users), 200
        return jsonify(f'There are no borger users in the database!'), 404