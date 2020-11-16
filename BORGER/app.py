from flask import Flask, jsonify, request
import sqlite3
from flask import g
import uuid
import datetime
import json

app = Flask(__name__)
DATABASE = 'borger.db'


###############################################
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
 ############################################### 
          
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

###############################################

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

###############################################

@app.route('/borger-user/<id>', methods=['PUT'])
def update_borgerUser(id):
    borger_id = str(id)
    new_UserId = str(request.json['UserId'])
    try:
        cur = get_db().cursor()
        cur.execute(f"SELECT 1 FROM BorgerUser WHERE UserId=?", (borger_id,))
        record = cur.fetchone()
        if record is None:
            return jsonify(f'User with the ID: {borger_id} does not exist!'), 404
        else:
            cur.execute("UPDATE Address SET BorgerUserId = ? WHERE BorgerUserId = ?", (new_UserId,borger_id))
            cur.execute("UPDATE FROM BorgerUser SET UserId = ? WHERE UserId = ?", (new_UserId,borger_id))            
            get_db().commit()
            return jsonify(f'User with the new ID: {borger_id} has succesfully been updated!'), 200
    except Exception as e:
        print(f"*** Error in /borger-user (create new borger) ***: \n{e}")
        return jsonify("Server error: sorry cant update the Borger!"), 500

###############################################

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