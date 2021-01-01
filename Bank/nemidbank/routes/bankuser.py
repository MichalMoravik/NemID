from flask import request, jsonify
from datetime import datetime
# from __init__.py file import app - for routes (@app.route)
from nemidbank import app
from nemidbank.dbconfig import get_db
import json


@app.route('/bank-user', methods=['POST'])
def create_bank_user():
    """Creates a new bank user, adds this user to the database.

    Returns:
        Various json strings and status codes based on different conditions.
    """
    try:
        user_id = int(request.json['userId'])
    except Exception as e:
        print(f"*** Error in routes/bank-user/create_bank_user() ***: \n{e}")
        return jsonify("Check spelling and data types of request body elements!"), 400 
    else:
        try:
            cur = get_db().cursor()
            
            cur.execute(f"SELECT 1 FROM BankUser WHERE UserId=?", (user_id,))
            record = cur.fetchone()
            if record is not None:
                return jsonify(f'User with id: {user_id} is already registered in the system!'), 403
            
            current_datetime = datetime.now().strftime("%B %d, %Y %I:%M%p")
            
            cur.execute('INSERT INTO BankUser(UserId, CreatedAt, ModifiedAt) VALUES (?,?,?)', 
                        (user_id, current_datetime, current_datetime))
            get_db().commit()
        except Exception as e:
            print(f"*** Error in routes/bank-user/create_bank_user() ***: \n{e}")
            return jsonify("Server error: unable to register a new bank user!"), 500
        else:
            return jsonify(f"A new bank user with user id: {user_id} was successfully registered!"), 201


@app.route('/bank-user/<id>', methods=['PUT'])
def update_bank_user(id):
    """Updates a bank user with specified Id.

    Args:
        id: taken from the route URL e.g. bankuser/1

    Returns:
        Various json strings and status codes based on different conditions.
    """
    try:
        id = int(id)
    except Exception as e:
        print(f"*** Error in routes/bank-user/update_bank_user() ***: \n{e}")
        return jsonify("Server error: Specified id could not be parsed into integer!"), 422 
    else:
        try:
            current_datetime = datetime.now().strftime("%B %d, %Y %I:%M%p")
            cur = get_db().cursor()
            
            cur.execute('UPDATE BankUser SET ModifiedAt=? WHERE Id=?', 
                        (current_datetime, id, ))
        except Exception as e:
            print(f"*** Error in routes/bank-user/update_bank_user() ***: \n{e}")
            return jsonify("Server error: Cannot update the bank user!"), 500
        else:
            if cur.rowcount == 1:
                try:
                    get_db().commit()
                except Exception as e:
                    print(f"*** Error in routes/bank-user/update_bank_user() ***: \n{e}")
                    return jsonify("Server error: Cannot update the bank user!"), 500
                else:
                    return jsonify(f'A bank user with id: {id} was updated!'), 200
            return jsonify(f'A bank user with id: {id} does not exists!'), 404


@app.route('/bank-user/<id>', methods=['DELETE'])
def delete_bank_user(id):
    """Deletes a bank user with specified Id.

    Args:
        id: taken from the route URL e.g. bankuser/1

    Returns:
        Various json strings and status codes based on different conditions.
    """
    try:
        id = int(id)     
    except Exception as e:
        print(f"*** Error in routes/bank-user/delete_bank_user() ***: \n{e}")
        return jsonify("Specified ID could not be parsed to integer!"), 422
    else:  
        try:
            cur = get_db().cursor()
            cur.execute("DELETE FROM BankUser WHERE Id=?", (id,))
        except Exception as e:
            print(f"*** Error in routes/user/delete_bank_user() ***: \n{e}")
            return jsonify("Server error: Cannot delete user!"), 500
        else:
            if cur.rowcount == 1:
                try:
                    get_db().commit()
                except Exception as e:
                    print(f"*** Error in routes/user/delete_bank_user() ***: \n{e}")
                    return jsonify("Server error: Cannot delete user!"), 500
                else:
                    return jsonify(f'User with id: {id} deleted!'), 200
            return jsonify(f'User with id {id} does not exists!'), 404
    

@app.route('/bank-user', methods=['GET'])
def get_bank_users():
    """Retrieves all user from the database.

    Returns:
        Various json strings and status codes based on different conditions.
        If successful, returns all the bank users and 200 status code.
    """
    try:
        cur = get_db().cursor()
        cur.execute("SELECT * FROM BankUser")
        rows = cur.fetchall()
    except Exception as e:
        print(f"*** Error in routes/user/get_bank_users() ***: \n{e}")
        return jsonify("Server error: Cannot get users!"), 500
    else: 
        if rows:
            users = [dict(user) for user in rows]
            return json.dumps(users), 200
        return jsonify(f'There are no bank users in the database!'), 404


@app.route('/bank-user/<id>', methods=['GET'])
def get_bank_user(id):    
    """Retrieves a bank user specified by Id.

    Args:
        id: taken from the route URL e.g. bankuser/1

    Returns:
        Various json strings and status codes based on different conditions.
        If successful, returns a bank user and 200 status code.
    """
    try:
        id = int(id)     
    except Exception as e:
        print(f"*** Error in routes/user/get_bank_user() ***: \n{e}")
        return jsonify("Specified ID could not be parsed to integer!"), 422
    else:
        try:
            cur = get_db().cursor()
            cur.execute("SELECT * FROM BankUser WHERE Id=?", (id,))
            row = cur.fetchone()
        except Exception as e:
            print(f"*** Error in routes/user/get_bank_user() ***: \n{e}")
            return jsonify("Server error: Cannot get user!"), 500
        else:
            if row is None:
                return jsonify(f'BankUser with id {id} does not exists'), 404
            user = dict(row)
            return json.dumps(user), 200