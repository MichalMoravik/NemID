from flask import request, jsonify
from datetime import datetime
from nemidskat import app
from nemidskat.dbconfig import get_db
import json

@app.route('/skatuser', methods=['POST'])
def create_skat_user():
    # Create a new skat user
    try:
        user_id = str(request.json['userId'])
        created_at = str(request.json['createdAt'])
        is_active = 1
    except Exception as e:
        print(f"*** Error in routes/skatuser/create_skat_user() ***: \n{e}")
        return jsonify("Check spelling and data types of request body elements!"), 400 
    else:
        try:
            cur = get_db().cursor()
            
            cur.execute(f"SELECT 1 FROM SkatUser WHERE UserId=?", (user_id,))
            record = cur.fetchone()
            if record is not None:
                return jsonify(f'User with id: {user_id} is already registered in the system!'), 403
            
            cur.execute('INSERT INTO SkatUser(UserId, CreatedAt, IsActive) VALUES (?,?,?)', 
                        (user_id, created_at, is_active))
            get_db().commit()
        except Exception as e:
            print(f"*** Error in routes/skatuser/create_skat_user() ***: \n{e}")
            return jsonify("Server error: unable to register a new skat user!"), 500
        else:
            return jsonify(f"A new skat user with user id: {user_id} was successfully registered!"), 201



@app.route('/skatuser', methods=['GET'])
def get_skat_users():
    #Get all users
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



@app.route('/skatuser/<id>', methods=['PUT'])
def update_skat_user(id):
    #Updates a skat user
    try:
        id = int(id)
        user_id = str(request.json['userId'])
        created_at = str(request.json['createdAt'])
        is_active = int(request.json['isActive'])
    except Exception as e:
        print(f"*** Error in routes/skatuser/update_skat_user() ***: \n{e}")
        return jsonify("Server error: Specified id could not be parsed into integer!"), 422 
    else:
        try:
            cur = get_db().cursor()
            
            cur.execute('UPDATE SkatUser SET UserId=?, CreatedAt=?, IsActive=? WHERE Id=?', 
                        (user_id, created_at, is_active, id, ))
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
            return jsonify(f'A skat user with id: {id} does not exists!'), 404



@app.route('/skatuser/<id>', methods=['DELETE'])
def delete_skat_user(id):
    #Deletes a skat user
    try:
        id = int(id)     
    except Exception as e:
        print(f"*** Error in routes/skatuser/delete_skat_user() ***: \n{e}")
        return jsonify("Server error: Specified ID could not be parsed to integer!"), 422
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
            return jsonify(f'Skat user with id {id} does not exists!'), 404




@app.route('/skatuser/<id>', methods=['GET'])
def get_skat_user(id):    
    #Gets a skat user by ID
    try:
        id = int(id)     
    except Exception as e:
        print(f"*** Error in routes/user/get_skat_user() ***: \n{e}")
        return jsonify("Server error: Specified ID could not be parsed to integer!"), 422
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
                return jsonify(f'Skat user with id {id} does not exists'), 404
            user = dict(row)
            return json.dumps(user), 200