from typing import Type
from flask import request, jsonify
from flask import json
# from __init__.py file import app - for routes (@app.route)
from nemidapi import app
import random
from datetime import datetime
from nemidapi.dbconfig import get_db

# 1. check if it exists
# 2. post request should return newly created item
# 3. validation
# 4. add everywhere UNIQUE
# 5. add everywhere comments

@app.route('/gender', methods=['POST'])
def create_gender():
    label = str(request.json['label']).lower()
    
    try:
        cur = get_db().cursor()
        
        cur.execute(f"SELECT * FROM Gender WHERE Label=?", (label,))
        record = cur.fetchone()
        if record is not None:
            return jsonify(f'Gender {label} already exists!'), 403
        
        cur.execute('INSERT INTO Gender(Label) VALUES (?)', (label,))
        get_db().commit()
    except Exception as e:
        print(f"************** Error **************: \n{e}")
        return jsonify("Server error: unable to create gender!"), 500
    else: 
        return jsonify(f'Gender {label} created!'), 201


# Update gender
@app.route('/gender/<id>', methods=['PUT'])
def update_gender(id):
    label = str(request.json['label'])

    try:
        cur = get_db().cursor()
        cur.execute('UPDATE Gender SET Label = ? WHERE id = ?', (label, id, ))
    except Exception as e:
        print(f"************** Error **************: \n{e}")
        return jsonify("Server error: Cannot update gender!"), 500
    else:
        if cur.rowcount == 1:
            try:
                get_db().commit()
            except Exception as e:
                print(f"************** Error **************: \n{e}")
                return jsonify("Server error: Cannot update gender!"), 500
            else:
                return jsonify(f'Gender with id: {id} updated!'), 200
        return jsonify(f'Gender with id {id} does not exists!'), 404


# Delete gender
@app.route('/gender/<id>', methods=['DELETE'])
def delete_gender(id):
    try:
        cur = get_db().cursor()
        cur.execute("DELETE FROM Gender WHERE Id=?", (id,))
    except Exception as e:
        print(f"************** Error **************: \n{e}")
        return jsonify("Server error: Cannot delete gender!"), 500
    else:
        if cur.rowcount == 1:
            try:
                get_db().commit()
            except Exception as e:
                print(f"************** Error **************: \n{e}")
                return jsonify("Server error: Cannot delete gender!"), 500
            else:
                return jsonify(f'Gender with id: {id} deleted!'), 200
        return jsonify(f'Gender with id {id} does not exists!'), 404
    

# Get all genders
@app.route('/gender', methods=['GET'])
def get_genders():
    try:
        cur = get_db().cursor()
        cur.execute("SELECT * FROM Gender")
        rows = cur.fetchall()
    except Exception as e:
        print(f"************** Error **************: \n{e}")
        return jsonify("Server error: Cannot get genders!"), 500
    else: 
        if rows:
            genders = [dict(gender) for gender in rows]
            return json.dumps(genders), 200
        return jsonify(f'There are no genders in the database!'), 404

# Get one gender
@app.route('/gender/<id>', methods=['GET'])
def get_gender(id):
    try:
        cur = get_db().cursor()
        cur.execute("SELECT * FROM Gender WHERE Id=? ORDER BY ROWID ASC LIMIT 1", (id,))
        row = cur.fetchone()
    except Exception as e:
        print(f"************** Error **************: \n{e}")
        return jsonify("Server error: Cannot get gender!"), 500
    else:
        if row is None:
            return jsonify(f'Gender with id {id} does not exists'), 404
        gender = dict(row)
        return json.dumps(gender), 200

