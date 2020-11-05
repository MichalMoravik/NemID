from typing import Type
from flask import request, jsonify
from flask import json
# from __init__.py file import app - for routes (@app.route)
from nemidapi import app
import random
from datetime import datetime
from nemidapi.dbconfig import get_db

######### HELPERS ##########
def check_if_gender_exists(cur, **kwargs):
    """Check if gender exists. Query either by label or id"""
    keys = list(kwargs.keys())
    values = list(kwargs.values())
    
    if len(keys) == 1 and 'label' in keys or 'id' in keys:
        cur.execute(f"SELECT * FROM Gender WHERE {keys[0].title()}=(?)", (values[0],))
    elif len(keys) > 0:
        raise ValueError(f"Check_if_gender_exists() got unexpected parameters' values")
    else:
        raise ValueError("Specify field you want to SELECT by")
    
    gender = cur.fetchone()
    if gender is None:
        return False
    return True


def return_results_from_db(cur, query, id=None):
    if id:
        cur.execute(query, (id,))
    else:
        cur.execute(query)
        
    result = [dict((cur.description[i][0], value) \
            for i, value in enumerate(row)) for row in cur.fetchall()]
    return (result[0] if result else None) if id else result


@app.route('/gender', methods=['POST'])
def create_gender():
    label = str(request.json['label']).lower()
    
    try:
        cur = get_db().cursor()
        if check_if_gender_exists(cur, label=label):
            return jsonify(f'{label} already exists'), 403
        cur.execute('INSERT INTO Gender(Label) VALUES (?)', (label,))
        get_db().commit()
    except Exception as e:
        print(f"************** Error **************: \n{e}")
        return jsonify("Server error: unable to create gender!"), 500
    else: 
        return jsonify(f'{label} gender created'), 200


# Update gender
@app.route('/gender/<id>', methods=['PUT'])
def update_gender(id):
    label = str(request.json['label'])

    try:
        cur = get_db().cursor()
        if check_if_gender_exists(cur, id=id) == False:
            return jsonify(f'Gender with id {id} does not exists'), 404
        cur.execute('UPDATE Gender SET Label = ? WHERE id = ?', (label,id, ))
        get_db().commit()
    except Exception as e:
        print(f"************** Error **************: \n{e}")
        return jsonify("Server error: Cannot update gender!"), 500
    else:
        return jsonify(f'Gender updated to: {label}'), 200


# Delete gender
@app.route('/gender/<id>', methods=['DELETE'])
def delete_gender(id):
    try:
        cur = get_db().cursor()
        if check_if_gender_exists(cur, id=id) == False:
            return jsonify(f'Gender with id {id} does not exists'), 404
        cur.execute("DELETE FROM Gender WHERE Id=?", (id,))
        get_db().commit()
    except Exception as e:
        print(f"************** Error **************: \n{e}")
        return jsonify("Server error: Cannot delete gender!"), 500
    else:
        return jsonify(f'Gender with id: {id} delete'), 200
    

# Get all genders
@app.route('/gender', methods=['GET'])
def get_genders():
    try:
        cur = get_db().cursor()
        genders = json.dumps(return_results_from_db(cur, "SELECT * FROM Gender"))
    except Exception as e:
        print(f"************** Error **************: \n{e}")
        return jsonify("Server error: Cannot get genders!"), 500
    else: 
        return genders, 200

# 1. check if it exists
# 2. post request should return newly created item
# 3. validation

# Get one gender
@app.route('/gender/<id>', methods=['GET'])
def get_gender(id):
    try:
        cur = get_db().cursor()
        if check_if_gender_exists(cur, id=id) == False:
            return jsonify(f'Gender with id {id} does not exists'), 404
        gender = json.dumps(return_results_from_db(cur, "SELECT * FROM Gender WHERE id=?", id))
    except Exception as e:
        print(f"************** Error **************: \n{e}")
        return jsonify("Server error: Cannot get gender!"), 500
    else:
        return gender, 200

