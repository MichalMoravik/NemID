from flask import request, jsonify
from datetime import datetime
from nemidskat import app
from nemidskat.dbconfig import get_db
import json


@app.route('/skatyear', methods=['POST'])
def create_skat_year():
    """Creates a new skat year. Checks if the skat year already exists. 
    If not, then it creates a new record in SkatUserYear (junction) table for each skat user. 
    It adds "IsPaid" property with an amount to to be paid by each skat user.

    Returns:
        Various json strings and status codes based on different conditions.
        If successful, creates a new skat year and adds all skat users to the created year.
        After that, returns 201 status code.
    """
    try:
        label = str(request.json['label'])
        start_date = str(request.json['startDate'])
        end_date = str(request.json['endDate']) 
    except Exception as e:
        print(f"*** Error in routes/skatyear/create_skat_year() ***: \n{e}")
        return jsonify("Check spelling and data types of request body elements!"), 400 
    else:
        try:
            cur = get_db().cursor()
            
            cur.execute(f"SELECT 1 FROM SkatYear WHERE Label=?", (label,))
            
            # checking if the skat year already exists in the database to prevent multiple same skat years
            record = cur.fetchone()
            if record is not None:
                return jsonify(f'Year with label: {label} is already registered in the system!'), 403
            
            # getting the current datetime
            current_datetime = datetime.now().strftime("%B %d, %Y %I:%M%p")
            
            # inserting a new skat year to the database
            cur.execute('INSERT INTO SkatYear(Label, CreatedAt, ModifiedAt, StartDate, EndDate) VALUES (?,?,?,?,?)', 
                        (label, current_datetime, current_datetime, start_date, end_date))
            # get id of the inserted row
            inserted_year_id = cur.lastrowid
            
            # select every skat user
            cur.execute(f"SELECT * FROM SkatUser")
            skat_users = cur.fetchall()
        
            # if there is no skat user in the database, return 404 
            if len(skat_users) == 0:
                return jsonify("There are no skat users in the database"), 404
            
            # for each skat user, create a new record in SkatUserYear 
            for skat_user in skat_users:
                cur.execute(f'INSERT INTO SkatUserYear(SkatUserId, SkatYearId, UserId, IsPaid, Amount) VALUES (?,?,?,?,?)',
                            (int(skat_user[0]), inserted_year_id, str(skat_user[1]), 0, 0))
                
            # commiting at the end serves as transaction END
            # in sqlite3, all commands executed before .commit() are considered as part of the transaction operation
            get_db().commit()
            
        except Exception as e:
            print(f"*** Error in routes/skatyear/create_skat_year() ***: \n{e}")
            return jsonify("Server error: unable to create a new skat year!"), 500
        else:
            return jsonify("A new skat year was successfully added. " +
                        "All skat users were attached to the new skat year."), 201


@app.route('/skatyear/<id>', methods=['PUT'])
def update_skat_year(id):
    """Updates the skat year with the specified id.

    Args:
        id (int): skat year ID taken from the route URL e.g. skatyear/1

    Returns:
        Various json strings and status codes based on different conditions.
        If successful, updates the skat year and returns the success message and 200 status code.
    """
    try:
        id = int(id)
        label = str(request.json['label'])
        start_date = str(request.json['startDate'])
        end_date = str(request.json['endDate'])
    except Exception as e:
        print(f"*** Error in routes/skatyear/update_skat_year() ***: \n{e}")
        return jsonify("Check spelling and data types of request body elements!"), 400 
    else:
        try:
            cur = get_db().cursor()
            
            # getting the current datetime
            modified_at = datetime.now().strftime("%B %d, %Y %I:%M%p")
            
            cur.execute('UPDATE SkatYear SET Label=?, ModifiedAt=?, StartDate=?, EndDate=? WHERE Id=?', 
                        (label, modified_at, start_date, end_date, id, ))
        except Exception as e:
            print(f"*** Error in routes/skatyear/update_skat_year() ***: \n{e}")
            return jsonify("Server error: Cannot update the skat year!"), 500
        else:
            # if we successfully updated one (and only one) row, then proceed
            if cur.rowcount == 1:
                try:
                    get_db().commit()
                except Exception as e:
                    print(f"*** Error in routes/skatyear/update_skat_year() ***: \n{e}")
                    return jsonify("Server error: Cannot update the skat year!"), 500
                else:
                    return jsonify(f'A skat year with id: {id} was updated!'), 200
            return jsonify(f'A skat year with id: {id} does not exists!'), 404


@app.route('/skatyear/<id>', methods=['DELETE'])
def delete_skat_year(id):
    """Deletes the skat year with the specified id.

    Args:
        id (int): skat user ID taken from the route URL e.g. skatyear/1

    Returns:
        Various json strings and status codes based on different conditions.
        If successful, deletes the skat year and returns the success message and 200 status code.
    """
    try:
        id = int(id)     
    except Exception as e:
        print(f"*** Error in routes/skatyear/delete_skat_year() ***: \n{e}")
        return jsonify("Specified ID could not be parsed to integer!"), 422
    else:  
        try:
            cur = get_db().cursor()
            cur.execute("DELETE FROM SkatYear WHERE Id=?", (id,))
        except Exception as e:
            print(f"*** Error in routes/skatyear/delete_skat_year() ***: \n{e}")
            return jsonify("Server error: Cannot delete the skat year!"), 500
        else:
            if cur.rowcount == 1:
                try:
                    get_db().commit()
                except Exception as e:
                    print(f"*** Error in routes/skatyear/delete_skat_year() ***: \n{e}")
                    return jsonify("Server error: Cannot delete the skat year!"), 500
                else:
                    return jsonify(f'Skat year with id: {id} deleted!'), 200
            return jsonify(f'Skat year with id {id} does not exists!'), 404


@app.route('/skatyear/<id>', methods=['GET'])
def get_skat_year(id):    
    """Retrieves a skat year with the specified id from the database.

    Args:
        id (int): skat year ID taken from the route URL e.g. skatyear/1

    Returns:
        Various json strings and status codes based on different conditions.
        If successful, returns the skat year (JSON) and 200 status code.
    """
    try:
        id = int(id)     
    except Exception as e:
        print(f"*** Error in routes/skatyear/get_skat_year() ***: \n{e}")
        return jsonify("Specified ID could not be parsed to integer!"), 422
    else:
        try:
            cur = get_db().cursor()
            cur.execute("SELECT * FROM SkatYear WHERE Id=?", (id,))
            row = cur.fetchone()
        except Exception as e:
            print(f"*** Error in routes/skatyear/get_skat_year() ***: \n{e}")
            return jsonify("Server error: Cannot get skatyear!"), 500
        else:
            if row is None:
                return jsonify(f'Skat year with id {id} does not exists'), 404
            year = dict(row)
            return json.dumps(year), 200


@app.route('/skatyear', methods=['GET'])
def get_skat_years():
    """Retrieves all skat years from the database.

    Returns:
        Various json strings and status codes based on different conditions.
        If successful, returns all the skat years (JSON) and 200 status code.
    """
    try:
        cur = get_db().cursor()
        cur.execute("SELECT * FROM SkatYear")
        rows = cur.fetchall()
    except Exception as e:
        print(f"*** Error in routes/skatyear/get_skat_years() ***: \n{e}")
        return jsonify("Server error: Cannot get skat years!"), 500
    else: 
        if rows:
            years = [dict(year) for year in rows]
            return json.dumps(years), 200
        return jsonify(f'There are no skat years in the database!'), 404