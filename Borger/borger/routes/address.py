from flask import request, jsonify
from datetime import datetime
# from __init__.py file import app - for routes (@app.route)
from borger import app
from borger.dbconfig import get_db
import json
import borger.validations.requestdata as val


@app.route('/address', methods=['POST'])
def create_address():
    """Creates a new address for the specified borger user.

    Returns:
        Various json strings and status codes based on different conditions.
        If successful, creates a new address and returns success message with 201 status code
    """
    try:
        borger_user_id = int(request.json['borgerUserId'])
        address = val.empty_validation(str(request.json['address']))
    except Exception as e:
        print(f"*** Error in routes/address/create_address() ***: \n{e}")
        return jsonify("Check spelling and data types of request body elements!"), 400 
    else:
        try:
            cur = get_db().cursor()
            
            # find out if the specified borger user exists
            cur.execute(f"SELECT 1 FROM BorgerUser WHERE Id=?", (borger_user_id,))
            record = cur.fetchone()
            if record is None:
                return jsonify(f'A borger user with id: {borger_user_id} does not exist!'), 404
            
            # if there is already existing and active address for this borger user, deactivate it
            cur.execute('UPDATE Address SET IsValid=? WHERE BorgerUserId=? AND IsValid=?', (0, borger_user_id, 1))
            
            # add a new address and active it
            current_datetime = datetime.now().strftime("%B %d, %Y %I:%M%p")
            cur.execute('INSERT INTO Address(Address, BorgerUserId, CreatedAt, IsValid) VALUES (?,?,?,?)',
                    (address, borger_user_id, current_datetime, 1))

            get_db().commit()
        except Exception as e:
            print(f"*** Error in routes/address/create_address() ***: \n{e}")
            return jsonify("Server error: unable to register a new address!"), 500
        else:
            return jsonify(f"A new address for borger user with id: {borger_user_id} was successfully registered!"), 201


@app.route('/address/<id>', methods=['PUT'])
def update_address(id):
    """Updates an address with the specified id

    Args:
        id: taken from the route URL e.g. address/1

    Returns:
        Various json strings and status codes based on different conditions.
        If successful, edits an address and returns success message with 200 status code
    """
    try:
        id = int(id)
        address = val.empty_validation(str(request.json['address']))
    except Exception as e:
        print(f"*** Error in routes/address/update_address() ***: \n{e}")
        return jsonify("Check spelling and data types of request body elements!"), 400 
    else:
        try:
            cur = get_db().cursor()            
            cur.execute('UPDATE Address SET Address=? WHERE Id=?', (address, id))
            
            if cur.rowcount == 1:
                get_db().commit()
                return jsonify(f'A borger address with id: {id} has been updated!'), 200
            return jsonify(f'A borger address with id: {id} does not exist!'), 404
        
        except Exception as e:
            print(f"*** Error in routes/address/update_address() ***: \n{e}")
            return jsonify("Server error: Cannot update the address!"), 500            


@app.route('/address/<id>', methods=['DELETE'])
def delete_address(id):
    """Removes an address with the specified id from the database.

    Args:
        id: taken from the route URL e.g. address/1

    Returns:
        Various json strings and status codes based on different conditions.
        If successful, returns a success message and 200 status code
    """
    try:
        id = int(id)     
    except Exception as e:
        print(f"*** Error in routes/address/delete_address() ***: \n{e}")
        return jsonify("Specified ID could not be parsed to integer!"), 422
    else:  
        try:
            cur = get_db().cursor()
            cur.execute("DELETE FROM Address WHERE Id=?", (id,))
            
            if cur.rowcount == 1:
                get_db().commit()
                return jsonify(f'Address with id: {id} deleted!'), 200
            return jsonify(f'Address with id {id} does not exist!'), 404
            
        except Exception as e:
            print(f"*** Error in routes/address/delete_address() ***: \n{e}")
            return jsonify("Server error: Cannot delete the address!"), 500            
    

@app.route('/address', methods=['GET'])
def get_addresses():
    """Retrieves all borger addresses from the database.

    Returns:
        Various json strings and status codes based on different conditions.
        If successful, returns all addresses (JSON) and 200 status code.
    """
    try:
        cur = get_db().cursor()
        cur.execute("SELECT * FROM Address")
        rows = cur.fetchall()
    except Exception as e:
        print(f"*** Error in routes/address/get_addresses() ***: \n{e}")
        return jsonify("Server error: Cannot get addresses!"), 500
    else: 
        if rows:
            addresses = [dict(address) for address in rows]
            return json.dumps(addresses), 200
        return jsonify(f'There are no addresses in the database!'), 404


@app.route('/address/<id>', methods=['GET'])
def get_address(id):   
    """Retrieves an address with the specified ID from the database.
    
    Args:
        id: address ID taken from the route URL e.g. address/1

    Returns:
        Various json strings and status codes based on different conditions.
        If successful, returns the address (JSON) and 200 status code.
    """ 
    try:
        id = int(id)     
    except Exception as e:
        print(f"*** Error in routes/address/get_address() ***: \n{e}")
        return jsonify("Specified ID could not be parsed to integer!"), 422
    else:
        try:
            cur = get_db().cursor()
            cur.execute("SELECT * FROM Address WHERE Id=?", (id,))
            row = cur.fetchone()
        except Exception as e:
            print(f"*** Error in routes/address/get_address() ***: \n{e}")
            return jsonify("Server error: Cannot get the address!"), 500
        else:
            if row is None:
                return jsonify(f'Address with id {id} does not exist'), 404
            address = dict(row)
            return json.dumps(address), 200
