from flask import request, jsonify
from datetime import datetime
from nemidskat import app
from nemidskat.dbconfig import get_db
import json


@app.route('/skatyear', methods=['POST'])
def create_skat_year():
    # Create a new skat year
    """
    The method takes a body of one Skatyear, check according to label if the skatyear already exists and creates a new skatyear. Then, it takes the id of the created skatyear and also ids of all users
    as foreign keys and for every entry from the user table, it creates an entry in the SkatUserYear table. The values for IsPaid and Amount in the SkatUserYear will be adjust in the pay-taxes endpoint.
    """
    try:
        label = str(request.json['label'])
        created_at = str(request.json['createdAt'])
        modified_at = str(request.json['modifiedAt'])
        start_date = str(request.json['startDate'])
        end_date = str(request.json['endDate']) 
    except Exception as e:
        print(f"*** Error in routes/skatyear/create_skat_year() ***: \n{e}")
        return jsonify("Check spelling and data types of request body elements!"), 400 
    else:
        try:
            cur = get_db().cursor()
            cur.execute(f"SELECT 1 FROM SkatYear WHERE Label=?", (label,))
            record = cur.fetchone()
            if record is not None:
                return jsonify(f'Year with label: {label} is already registered in the system!'), 403
            cur.execute('INSERT INTO SkatYear(Label, CreatedAt, ModifiedAt, StartDate, EndDate) VALUES (?,?,?,?,?)', 
                        (label, created_at, modified_at, start_date, end_date))
            get_db().commit()
        except Exception as e:
            print(f"*** Error in routes/skatyear/create_skat_year() ***: \n{e}")
            return jsonify("Server error: unable to create a new skat year!"), 500
        else:
           # return jsonify(f"A new skat year with label: {label} was successfully registered!"), 201
            try:
                cur.execute(f"SELECT * FROM SkatUser")
                skatuser_rows = cur.fetchall()
                cur.execute(f"SELECT Id FROM SkatYear WHERE Label = ?",(label,))
                skatyear_id = cur.fetchone()[0]
            except:
                print(f"*** Error in routes/skatyear/create_skat_year() ***: \n{e}")
                return jsonify("Server error: unable to select from skatuser or skatyear!"), 404
            else:
                if skatuser_rows:
                    for skatuser in skatuser_rows:
                        cur.execute(f'INSERT INTO SkatUserYear(SkatUserId, SkatYearId, UserId, IsPaid, Amount) VALUES (?,?,?,?,?)',(int(skatuser[0]), skatyear_id, str(skatuser[1]),0,100))
                        get_db().commit()    
                    return jsonify("Skatyear and Skatuseryears insterted according to Skatusers!"),200



@app.route('/skatyear', methods=['GET'])
def get_skat_years():
    #Get all years
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



@app.route('/skatyear/<id>', methods=['PUT'])
def update_skat_year(id):
    #Updates a skat year
    try:
        id = int(id)
        label = str(request.json['label'])
        created_at = str(request.json['createdAt'])
        modified_at = str(request.json['modifiedAt'])
        start_date = str(request.json['startDate'])
        end_date = str(request.json['endDate'])
    except Exception as e:
        print(f"*** Error in routes/skatyear/update_skat_year() ***: \n{e}")
        return jsonify("Server error: Specified id could not be parsed into integer!"), 422 
    else:
        try:
            cur = get_db().cursor()
            
            cur.execute('UPDATE SkatYear SET Label=?, CreatedAt=?, ModifiedAt=?, StartDate=?, EndDate=? WHERE Id=?', 
                        (label, created_at, modified_at, start_date, end_date, id, ))
        except Exception as e:
            print(f"*** Error in routes/skatyear/update_skat_year() ***: \n{e}")
            return jsonify("Server error: Cannot update the skat year!"), 500
        else:
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
    #Deletes a skat year
    try:
        id = int(id)     
    except Exception as e:
        print(f"*** Error in routes/skatyear/delete_skat_year() ***: \n{e}")
        return jsonify("Server error: Specified ID could not be parsed to integer!"), 422
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
    #Gets a skat year by ID
    try:
        id = int(id)     
    except Exception as e:
        print(f"*** Error in routes/skatyear/get_skat_year() ***: \n{e}")
        return jsonify("Server error: Specified ID could not be parsed to integer!"), 422
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
