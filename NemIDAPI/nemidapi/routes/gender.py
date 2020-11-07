from flask import request, jsonify
from flask import json
# from __init__.py file import app - for routes (@app.route)
from nemidapi import app
from nemidapi.dbconfig import get_db

@app.route('/gender', methods=['POST'])
def create_gender():
    """Creates a new gender, then stores it in the database

    Returns:
        json string and status code based on different conditions
    """
    try:
        label = str(request.json['label']).lower()        
    except Exception as e:
        print(f"*** Error in routes/gender/create_gender() *** \n{e}")
        return jsonify("Server error: Check JSON spelling, parsing process, or similar!"), 500
    else:  
        try:
            cur = get_db().cursor()
            
            cur.execute(f"SELECT 1 FROM Gender WHERE Label=?", (label,))
            record = cur.fetchone()
            if record is not None:
                return jsonify(f'Gender {label} already exists!'), 403
            
            cur.execute('INSERT INTO Gender(Label) VALUES (?)', (label,))
            get_db().commit()
        except Exception as e:
            print(f"*** Error in routes/gender/create_gender() *** \n{e}")
            return jsonify("Server error: unable to create gender!"), 500
        else: 
            return jsonify(f'Gender {label} created!'), 201


@app.route('/gender/<id>', methods=['PUT'])
def update_gender(id):
    """Updates gender in the database.

    Args:
        id: taken from the route URL e.g. ...gender/1

    Returns:
        json string and status code based on different conditions
    """
    try:
        label = str(request.json['label']).lower() 
        id = int(id)
    except Exception as e:
        print(f"*** Error in routes/gender/update_gender() *** \n{e}")
        return jsonify("Server error: Check JSON spelling, parsing process, or similar!"), 500
    else:  
        try:            
            cur = get_db().cursor()
            cur.execute('UPDATE Gender SET Label = ? WHERE Id = ?', (label, id, ))
        except Exception as e:
            print(f"*** Error in routes/gender/update_gender() *** \n{e}")
            return jsonify("Server error: Cannot update gender!"), 500
        else:
            if cur.rowcount == 1:
                try:
                    get_db().commit()
                except Exception as e:
                    print(f"*** Error in routes/gender/update_gender() *** \n{e}")
                    return jsonify("Server error: Cannot update gender!"), 500
                else:
                    return jsonify(f'Gender with id: {id} updated!'), 200
            return jsonify(f'Gender with id {id} does not exists!'), 404


@app.route('/gender/<id>', methods=['DELETE'])
def delete_gender(id):
    """Removes a gender from the database

    Args:
        id: taken from the route URL e.g. ...gender/1

    Returns:
        json string and status code based on different conditions
    """
    try:
        id = int(id)     
    except Exception as e:
        print(f"*** Error in routes/gender/delete_gender *** \n{e}")
        return jsonify("Server error: This ID could not be parsed to integer!"), 500
    else:  
        try:
            cur = get_db().cursor()
            cur.execute("DELETE FROM Gender WHERE Id=?", (id,))
        except Exception as e:
            print(f"*** Error in routes/gender/delete_gender *** \n{e}")
            return jsonify("Server error: Cannot delete gender!"), 500
        else:
            if cur.rowcount == 1:
                try:
                    get_db().commit()
                except Exception as e:
                    print(f"*** Error in routes/gender/delete_gender *** \n{e}")
                    return jsonify("Server error: Cannot delete gender!"), 500
                else:
                    return jsonify(f'Gender with id: {id} deleted!'), 200
            return jsonify(f'Gender with id {id} does not exists!'), 404
    

@app.route('/gender', methods=['GET'])
def get_genders():
    """Pulls all genders from the database

    Returns:
        json string and status code based on different conditions
    """
    try:
        cur = get_db().cursor()
        cur.execute("SELECT * FROM Gender")
        rows = cur.fetchall()
    except Exception as e:
        print(f"*** Error in routes/gender/get_genders() *** \n{e}")
        return jsonify("Server error: Cannot get genders!"), 500
    else: 
        if rows:
            genders = [dict(gender) for gender in rows]
            return json.dumps(genders), 200
        return jsonify(f'There are no genders in the database!'), 404


@app.route('/gender/<id>', methods=['GET'])
def get_gender(id):
    """Pulls specific gender from the database.

    Args:
        id: taken from the route URL e.g. ...gender/1

    Returns:
        json string and status code based on different conditions
    """
    try:
        id = int(id)     
    except Exception as e:
        print(f"*** Error in routes/gender/get_gender() *** \n{e}")
        return jsonify("Server error: This ID could not be parsed to integer!"), 500
    else:
        try:
            cur = get_db().cursor()
            cur.execute("SELECT * FROM Gender WHERE Id=?", (id,))
            row = cur.fetchone()
        except Exception as e:
            print(f"*** Error *** \n{e}")
            return jsonify("Server error: Cannot get gender!"), 500
        else:
            if row is None:
                return jsonify(f'Gender with id {id} does not exists'), 404
            gender = dict(row)
            return json.dumps(gender), 200

