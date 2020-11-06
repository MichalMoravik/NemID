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
    try:
        email = str(request.json['email']).lower()
        cpr = str(request.json['cpr'])
        created_at = datetime.now().strftime("%B %d, %Y %I:%M%p")
        modified_at = datetime.now().strftime("%B %d, %Y %I:%M%p")
        gender_id = int(request.json['genderId'])
        nem_id = generate_nem_ID_number(cpr) 
        password_hash = hashlib.sha256(str.encode(request.json['passwordHash'])).hexdigest()
    except Exception as e:
        print(f"************** Error **************: \n{e}")
        return jsonify("Server error: Check JSON spelling, parsing process, or similar!"), 500
    else:  
        try:
            cur = get_db().cursor()
            
            cur.execute(f"SELECT * FROM User WHERE CPR=?", (cpr,))
            record = cur.fetchone()
            if record is not None:
                return jsonify(f'User with CPR {cpr} already exists!'), 403
            
            cur.execute('INSERT INTO User(Email, NemId, CPR, CreatedAt, ModifiedAt, GenderId) VALUES (?,?,?,?,?,?)', 
                        (email, nem_id, cpr, created_at, modified_at, gender_id))
            cur.execute('INSERT INTO Password(PasswordHash, UserId, CreatedAt, IsValid) VALUES (?,?,?,?)', 
                        (password_hash, cur.lastrowid, created_at, 1))
            get_db().commit()
        except Exception as e:
            print(f"************** Error **************: \n{e}")
            return jsonify("Server error: unable to register user!"), 500
        else:
            return jsonify(f"User with CPR {cpr} was created!"), 201


# Update user
@app.route('/user/<id>', methods=['PUT'])
def update_user(id):
    try:
        email = str(request.json['email']).lower()
        cpr = str(request.json['cpr']).lower()
        modified_at = datetime.now().strftime("%B %d, %Y %I:%M%p")
        gender_id = int(request.json['genderId'])
        nem_id = generate_nem_ID_number(cpr)
        id = int(id)       
    except Exception as e:
        print(f"************** Error **************: \n{e}")
        return jsonify("Server error: Check JSON request body spelling, \
                    parsing process, or similar!"), 500
    else:  
        try:
            cur = get_db().cursor()
            cur.execute('UPDATE User SET Email=?, CPR=?, ModifiedAt=?, GenderId=?, NemId=?  WHERE Id=?', 
                        (email, cpr, modified_at, gender_id, nem_id, id, ))
        except Exception as e:
            print(f"************** Error **************: \n{e}")
            return jsonify("Server error: Cannot update user!"), 500
        else:
            if cur.rowcount == 1:
                try:
                    get_db().commit()
                except Exception as e:
                    print(f"************** Error **************: \n{e}")
                    return jsonify("Server error: Cannot update user!"), 500
                else:
                    return jsonify(f'User with id: {id} updated!'), 200
            return jsonify(f'User with id {id} does not exists!'), 404


# Delete user
@app.route('/user/<id>', methods=['DELETE'])
def delete_user(id):
    try:
        id = int(id)     
    except Exception as e:
        print(f"************** Error **************: \n{e}")
        return jsonify("Server error: This ID could not be parsed to integer!"), 500
    else:  
        try:
            cur = get_db().cursor()
            cur.execute("DELETE FROM User WHERE Id=?", (id,))
        except Exception as e:
            print(f"************** Error **************: \n{e}")
            return jsonify("Server error: Cannot delete user!"), 500
        else:
            if cur.rowcount == 1:
                try:
                    get_db().commit()
                except Exception as e:
                    print(f"************** Error **************: \n{e}")
                    return jsonify("Server error: Cannot delete user!"), 500
                else:
                    return jsonify(f'User with id: {id} deleted!'), 200
            return jsonify(f'User with id {id} does not exists!'), 404
    

# Get all users
@app.route('/user', methods=['GET'])
def get_users():
    try:
        cur = get_db().cursor()
        cur.execute("SELECT * FROM User")
        rows = cur.fetchall()
    except Exception as e:
        print(f"************** Error **************: \n{e}")
        return jsonify("Server error: Cannot get users!"), 500
    else: 
        if rows:
            users = [dict(user) for user in rows]
            return json.dumps(users), 200
        return jsonify(f'There are no users in the database!'), 404

# Get one user
@app.route('/user/<id>', methods=['GET'])
def get_user(id):
    try:
        id = int(id)     
    except Exception as e:
        print(f"************** Error **************: \n{e}")
        return jsonify("Server error: This ID could not be parsed to integer!"), 500
    else:
        try:
            cur = get_db().cursor()
            cur.execute("SELECT * FROM User WHERE Id=?", (id,))
            row = cur.fetchone()
        except Exception as e:
            print(f"************** Error **************: \n{e}")
            return jsonify("Server error: Cannot get user!"), 500
        else:
            if row is None:
                return jsonify(f'User with id {id} does not exists'), 404
            user = dict(row)
            return json.dumps(user), 200



