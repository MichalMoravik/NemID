from flask import request, jsonify
from datetime import datetime
import requests
from skat import app
from skat.dbconfig import get_db
import json


# HELPERS
def get_tax_amount_for_user(start_date_str: str, end_date_str: str, user_id: int): 
    """Returns taxes that need to be paid for the specific user (user_id) and
    in the specific period (between start_date and the end_date)

    Args:
        start_date_str (str): start date in the string form
        end_date_str (str): end date in the string form
        user_id (int): a user id 

    Returns:
        tax_amount (int): taxes which need to be paid by the user
    """
    # make a request to the bank system. Pass user id and get all deposits for that user   
    r = requests.get(f'http://bank:81/user-deposits/{user_id}')
    # if the user has a bank account and 
    # at least one deposit between the start and end date, then proceed
    if r.ok:
        deposits = r.json()
        # total_deposit_amount is the total amount (all deposits counted) 
        # between the start and the end date
        total_deposit_amount = 0
        
        for deposit in deposits:
            # get date and amount of each deposit
            deposit_date_str = deposit['CreatedAt']
            deposit_amount = deposit['Amount']
            # convert the string dates into date form
            deposit_date = datetime.strptime(deposit_date_str, "%B %d, %Y %I:%M%p")
            start_date = datetime.strptime(start_date_str, "%B %d, %Y %I:%M%p")
            end_date = datetime.strptime(end_date_str, "%B %d, %Y %I:%M%p")
            
            # check if the date of the deposit is between start and end date,
            # if yes, add its amount to the total deposit amount
            if start_date <= deposit_date <= end_date:
                # count all amounts together
                total_deposit_amount += deposit_amount
        
        # send request with the total_deposit_amount for the specific period
        # to the serverless function to count the tax
        response = requests.post('http://functions:80/api/skattaxcalculator', json={"money": total_deposit_amount})
        tax = response.json()
        # return how much taxes need to be paid
        tax_amount = tax['tax_money']
        return tax_amount

    # if the user does not have any deposits or bank account yet
    # then we suppose the user does not have any income, and so, 
    # the user doesn't need to pay any taxes (return 0)
    else:
        return 0


@app.route('/year', methods=['POST'])
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
        print(f"*** Error in routes/year/create_skat_year() ***: \n{e}")
        return jsonify("Check spelling and data types of request body elements!"), 400 
    else:
        try:
            cur = get_db().cursor()
            
            cur.execute(f"SELECT 1 FROM SkatYear WHERE Label=?", (label,))
            
            # checking if the skat year already exists in the database to prevent multiple same skat years
            record = cur.fetchone()
            if record is not None:
                return jsonify(f'Year with label: {label} is already registered in the system!'), 200
            
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
                # get the tax amount a user needs to paid for the period
                tax_amount = get_tax_amount_for_user(start_date, end_date, skat_user['UserId'])
                
                # lambda returns 0 (boolean, is not paid) if the tax_amount is more than 0
                # if tax_amount is 0, the user doesn't need to pay anything, so
                # it is automatically considered as paid
                is_paid = lambda x: 0 if x > 0 else 1
                
                cur.execute(f'INSERT INTO SkatUserYear(SkatUserId, SkatYearId, IsPaid, Amount) VALUES (?,?,?,?)',
                            (int(skat_user['Id']), inserted_year_id, is_paid(tax_amount), tax_amount))
                
            # commiting at the end serves as transaction END
            # in sqlite3, all commands executed before .commit() are considered as part of the transaction operation
            get_db().commit()
            
        except Exception as e:
            print(f"*** Error in routes/year/create_skat_year() ***: \n{e}")
            return jsonify("Server error: unable to create a new skat year!"), 500
        else:
            return jsonify("A new skat year was successfully added. " +
                        "All skat users were attached to the new skat year."), 201
            

@app.route('/year/<id>', methods=['PUT'])
def update_skat_year(id):
    """Updates the skat year with the specified id.

    Args:
        id (int): skat year ID taken from the route URL e.g. year/1

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
        print(f"*** Error in routes/year/update_skat_year() ***: \n{e}")
        return jsonify("Check spelling and data types of request body elements!"), 400 
    else:
        try:
            cur = get_db().cursor()
            
            # getting the current datetime
            modified_at = datetime.now().strftime("%B %d, %Y %I:%M%p")
            
            cur.execute('UPDATE SkatYear SET Label=?, ModifiedAt=?, StartDate=?, EndDate=? WHERE Id=?', 
                        (label, modified_at, start_date, end_date, id, ))
            
            # if we successfully updated one (and only one) row, then proceed
            if cur.rowcount == 1:
                get_db().commit()
                return jsonify(f'A skat year with id: {id} was updated!'), 200
            return jsonify(f'A skat year with id: {id} does not exist!'), 404
            
        except Exception as e:
            print(f"*** Error in routes/year/update_skat_year() ***: \n{e}")
            return jsonify("Server error: Cannot update the skat year!"), 500            


@app.route('/year/<id>', methods=['DELETE'])
def delete_skat_year(id):
    """Deletes the skat year with the specified id.

    Args:
        id (int): skat user ID taken from the route URL e.g. year/1

    Returns:
        Various json strings and status codes based on different conditions.
        If successful, deletes the skat year and returns the success message and 200 status code.
    """
    try:
        id = int(id)     
    except Exception as e:
        print(f"*** Error in routes/year/delete_skat_year() ***: \n{e}")
        return jsonify("Specified ID could not be parsed to integer!"), 422
    else:  
        try:
            cur = get_db().cursor()
            cur.execute("DELETE FROM SkatYear WHERE Id=?", (id,))
            
            if cur.rowcount == 1:
                get_db().commit()
                return jsonify(f'Skat year with id: {id} deleted!'), 200
            return jsonify(f'Skat year with id {id} does not exist!'), 404
        
        except Exception as e:
            print(f"*** Error in routes/year/delete_skat_year() ***: \n{e}")
            return jsonify("Server error: Cannot delete the skat year!"), 500


@app.route('/year/<id>', methods=['GET'])
def get_skat_year(id):    
    """Retrieves a skat year with the specified id from the database.

    Args:
        id (int): skat year ID taken from the route URL e.g. year/1

    Returns:
        Various json strings and status codes based on different conditions.
        If successful, returns the skat year (JSON) and 200 status code.
    """
    try:
        id = int(id)     
    except Exception as e:
        print(f"*** Error in routes/year/get_skat_year() ***: \n{e}")
        return jsonify("Specified ID could not be parsed to integer!"), 422
    else:
        try:
            cur = get_db().cursor()
            cur.execute("SELECT * FROM SkatYear WHERE Id=?", (id,))
            row = cur.fetchone()
        except Exception as e:
            print(f"*** Error in routes/year/get_skat_year() ***: \n{e}")
            return jsonify("Server error: Cannot get year!"), 500
        else:
            if row is None:
                return jsonify(f'Skat year with id {id} does not exist'), 404
            year = dict(row)
            return json.dumps(year), 200


@app.route('/year', methods=['GET'])
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
        print(f"*** Error in routes/year/get_skat_years() ***: \n{e}")
        return jsonify("Server error: Cannot get skat years!"), 500
    else: 
        if rows:
            years = [dict(year) for year in rows]
            return json.dumps(years), 200
        return jsonify(f'There are no skat years in the database!'), 404