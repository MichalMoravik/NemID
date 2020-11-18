from flask import Flask, jsonify, request, g
import uuid
import datetime
import json
import sqlite3

DATABASE = 'borger.db'

app = Flask(__name__)

#################################################
# Database init
# DATABASE 
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
#################################################
# BORGER endpoints.
#-------------------------------------------------------
#WORKS!
@app.route('/borger-user', methods=['POST'])
def create_borgerUser():
    try:
        borger_id = str(uuid.uuid4())
        createdAt_now = str(datetime.datetime.now())
        cur = get_db().cursor()
        cur.execute("INSERT INTO BorgerUser(UserId, CreatedAt) VALUES (?,?)", (borger_id,createdAt_now))
        get_db().commit()
        return jsonify(f"Borger with ID {borger_id} was created!  \n datetime: {createdAt_now}"), 201
    except Exception as e:
        print(f"*** Error in /borger-user (create new borger) ***: \n{e}")
        return jsonify("Server error: unable to register Borger!"), 500

#-------------------------------------------------------
#WORKS!
@app.route('/borger-user/<id>', methods=['DELETE'])
def delete_borgerUser(id):
    borger_id = str(id)
    try:
        cur = get_db().cursor()
        cur.execute(f"SELECT 1 FROM BorgerUser WHERE UserId=?", (borger_id,))
        record = cur.fetchone()
        if record is None:
            return jsonify(f'User with the ID: {borger_id} does not exist!'), 404
        else:
            cur.execute("DELETE FROM Address WHERE BorgerUserId = ?", (borger_id,))
            cur.execute("DELETE FROM BorgerUser WHERE UserId = ?", (borger_id,))            
            get_db().commit()
            return jsonify(f'User with the ID: {borger_id} has succesfully been deleted!'), 200
    except Exception as e:
        print(f"*** Error in /borger-user (create new borger) ***: \n{e}")
        return jsonify("Server error: sorry cant delete the Borger!"), 500

#-------------------------------------------------------
#WORKS!
@app.route('/borger-user/<id>', methods=['PUT'])
def update_borgerUser(id):
    borger_id = str(id)
    new_UserId = str(request.json['UserId'])
    print(new_UserId)
    try:
        cur = get_db().cursor()
        cur.execute(f"SELECT 1 FROM BorgerUser WHERE UserId=?", (borger_id,))
        record = cur.fetchone()
        if record is None:
            return jsonify(f'User with the ID: {borger_id} does not exist!'), 404
        else:
            cur.execute("UPDATE Address SET BorgerUserId = ? WHERE BorgerUserId = ?", (new_UserId,borger_id))
            cur.execute("UPDATE BorgerUser SET UserId = ? WHERE UserId = ?", (new_UserId,borger_id))            
            get_db().commit()
            return jsonify(f'User with the new ID: {new_UserId} has succesfully been updated!'), 200
    except Exception as e:
        print(f"*** Error in /borger-user/<id> PUT (update borger) ***: \n{e}")
        return jsonify("Server error: sorry cant update the Borger!"), 500

#-------------------------------------------------------
# WORKS!
@app.route('/borger-user/<id>', methods=['GET'])
def get_borgerUser(id):
    borger_id = str(id)
    try:
        cur = get_db().cursor()
        cur.execute(f"SELECT UserId, CreatedAt FROM BorgerUser WHERE UserId=?", (borger_id,))
        record = cur.fetchone()
        if record is None:
            return jsonify(f'User with the ID: {borger_id} does not exist!'), 404
        else:
            user = dict(record)
            return json.dumps(user), 200
    except Exception as e:
        print(f"*** Error in /borger-user (create new borger) ***: \n{e}")
        return jsonify("Server error: sorry cant get the Borger!"), 500

###############################################
# Address Endpoint.

#-------------------------------------------------------
#WORKS
@app.route('/borger-address', methods=['POST'])
def create_borgerAddress():
    borger_id = str(request.json['UserId'])
    borger_address = str(request.json['Address'])
    createdAt_now = str(datetime.datetime.now())
    try:
        cur = get_db().cursor()
        cur.execute(f"SELECT 1 FROM BorgerUser WHERE UserId=?", (borger_id,))
        record = cur.fetchone()
        if record is None:
            return jsonify(f'cannot create address: {borger_id} does not exist!'), 404
        else:
            cur.execute("SELECT * from Address WHERE BorgerUserId = ? AND isvalid = 1", (borger_id,))
            record = cur.fetchall()
            if len(record) < 1:
                cur.execute("INSERT INTO Address(Address, CreatedAt, isvalid, BorgerUserId) VALUES (?,?,1,?)", (borger_address, createdAt_now,borger_id))          
                get_db().commit()
                return jsonify(f'Address has succesfully being added to the User with the ID: {borger_id}'), 200
            else:
                return jsonify(f'User already have a address registered, try updating it instead'), 409

    except Exception as e:
        print(f"*** Error in /borger-address (add address to borger) ***: \n{e}")
        return jsonify("Server error: unable to add Address to the Borger!"), 500

#-------------------------------------------------------
#WORKS!
@app.route('/borger-address/<id>', methods=['DELETE'])
def delete_borgerAddress(id):
    try:
        cur = get_db().cursor()
        cur.execute(f"SELECT 1 FROM Address WHERE Id=?", (id,))
        record = cur.fetchone()
        if record is None:
            return jsonify(f'cannot delete address with id: {id}, because it doesnt exits!'), 404
        else:
            cur.execute("DELETE FROM Address WHERE Id = ?", (id,))
            get_db().commit()
            return jsonify(f'Address with the id: {id}, has succesfully being deleted!'), 200

    except Exception as e:
        print(f"*** Error in /borger-address (delete address) ***: \n{e}")
        return jsonify("Server error: unable to delete Address!"), 500

#-------------------------------------------------------
#WORKS!
@app.route('/borger-address', methods=['PUT'])
def update_borgerAddress():
    borger_id = str(request.json['UserId'])
    borger_address = str(request.json['Address'])
    createdAt_now = str(datetime.datetime.now())
    try:
        cur = get_db().cursor()
        cur.execute(f"SELECT 1 FROM Address WHERE BorgerUserId=? AND isvalid = 1", (borger_id,))
        record = cur.fetchone()
        if record is None:
            return jsonify(f'No borger with id: {borger_id}, has a valid address!'), 404
        else:
            cur.execute("INSERT INTO Address(Address, CreatedAt, isvalid, BorgerUserId) VALUES (?,?,1,?)", (borger_address, createdAt_now,borger_id))  
            cur.execute(f"UPDATE Address SET isvalid = 0 WHERE BorgerUserId=? and CreatedAt != ?", (borger_id, createdAt_now))
            get_db().commit()
            return jsonify(f'Address has succesfully being updated!'), 200
    except Exception as e:
        print(f"*** Error in /borger-address (delete address) ***: \n{e}")
        return jsonify("Server error: unable to delete Address!"), 500

#-------------------------------------------------------
#WORKS!
@app.route('/borger-address', methods=['GET'])
def get_borgerAddress():
    borger_id = str(request.json['UserId'])
    try:
        cur = get_db().cursor()
        cur.execute(f"SELECT * FROM Address WHERE BorgerUserId=? AND isvalid = 1", (borger_id,))
        record = cur.fetchone()
        if record is None:
            return jsonify(f'No borger with id: {borger_id}, has a valid address!'), 404
        else:
            address = dict(record)
            return json.dumps(address), 200
    except Exception as e:
        print(f"*** Error in /borger-address (get address) ***: \n{e}")
        return jsonify("Server error: unable to get Address!"), 500



# Run app
if __name__ == "__main__":
    app.run(port=5555, debug=True)
