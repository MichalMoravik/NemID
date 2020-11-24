from flask import request, jsonify
from datetime import datetime
# from __init__.py file import app - for routes (@app.route)
from nemidbank import app
from nemidbank.dbconfig import get_db
import json


@app.route('/account', methods=['POST'])
def create_bank_account():
    """Creates a unique bank account for the specified bank user.

    Returns:
        Various json strings and status codes based on different conditions.
    """
    try:
        bank_user_id = int(request.json['bankUserId'])
        account_number = str(request.json['accountNo'])
        is_student = int(request.json['isStudent'])
        created_at = datetime.now().strftime("%B %d, %Y %I:%M%p")
        modified_at = datetime.now().strftime("%B %d, %Y %I:%M%p")
    except Exception as e:
        print(f"*** Error in routes/account/create_bank_account() ***: \n{e}")
        return jsonify("Check spelling and data types of request body elements!"), 400 
    else:
        try:
            cur = get_db().cursor()
            
            # check if is_student value is either 1 or 0
            if is_student != 0 and is_student != 1:
                return jsonify(f"isStudent has a wrong value. Use either 0 or 1. {is_student}"), 422
            
            # find out if the specified bank user exists
            cur.execute(f"SELECT 1 FROM BankUser WHERE Id=?", (bank_user_id,))
            record = cur.fetchone()
            if record is None:
                return jsonify(f'A bank user with id: {bank_user_id} does not exist!'), 404
            
            # find out if the bank user already has a bank account. If yes, return 403
            cur.execute(f"SELECT 1 FROM Account WHERE BankUserId=?", (bank_user_id,))
            record = cur.fetchone()
            if record is not None:
                return jsonify(f'A bank user with id: {bank_user_id} already has an account!'), 403
            
            cur.execute('INSERT INTO Account(BankUserId, AccountNo, isStudent, CreatedAt, ModifiedAt, Amount) VALUES (?,?,?,?,?,0)', 
                (bank_user_id, account_number, is_student, created_at, modified_at))
            get_db().commit()
        except Exception as e:
            print(f"*** Error in routes/account/create_bank_account() ***: \n{e}")
            return jsonify("Server error: unable to register a new bank account!"), 500
        else:
            return jsonify(f"A new bank account for bank user with id: {bank_user_id} was successfully registered!"), 201


@app.route('/account/<id>', methods=['PUT'])
def update_bank_account(id):
    """Updates a bank account with specified Id

    Args:
        id: taken from the route URL e.g. account/1

    Returns:
        Various json strings and status codes based on different conditions.
    """
    try:
        id = int(id)
        modified_at = datetime.now().strftime("%B %d, %Y %I:%M%p")
        is_student = int(request.json['isStudent'])
    except Exception as e:
        print(f"*** Error in routes/account/update_bank_account() ***: \n{e}")
        return jsonify("Check spelling and data types of request body elements!"), 400 
    else:
        try:
            cur = get_db().cursor()
            
            cur.execute('UPDATE Account SET isStudent=?, ModifiedAt=? WHERE Id=?', 
                        (is_student, modified_at, id))
        except Exception as e:
            print(f"*** Error in routes/account/update_bank_account() ***: \n{e}")
            return jsonify("Server error: Cannot update the bank user!"), 500
        else:
            if cur.rowcount == 1:
                try:
                    get_db().commit()
                except Exception as e:
                    print(f"*** Error in routes/account/update_bank_account() ***: \n{e}")
                    return jsonify("Server error: Cannot update the bank account!"), 500
                else:
                    return jsonify(f'A bank account with id: {id} was updated!'), 200
            return jsonify(f'A bank account with id: {id} does not exists!'), 404


@app.route('/account/<id>', methods=['DELETE'])
def delete_bank_account(id):
    """Removes a bank account with specified Id from the database.

    Args:
        id: taken from the route URL e.g. account/1

    Returns:
        Various json strings and status codes based on different conditions.
    """
    try:
        id = int(id)     
    except Exception as e:
        print(f"*** Error in routes/account/delete_bank_account() ***: \n{e}")
        return jsonify("Server error: Specified ID could not be parsed to integer!"), 422
    else:  
        try:
            cur = get_db().cursor()
            cur.execute("DELETE FROM Account WHERE Id=?", (id,))
        except Exception as e:
            print(f"*** Error in routes/account/delete_bank_account() ***: \n{e}")
            return jsonify("Server error: Cannot delete the bank account!"), 500
        else:
            if cur.rowcount == 1:
                try:
                    get_db().commit()
                except Exception as e:
                    print(f"*** Error in routes/account/delete_bank_account() ***: \n{e}")
                    return jsonify("Server error: Cannot delete the bank account!"), 500
                else:
                    return jsonify(f'Bank account with id: {id} deleted!'), 200
            return jsonify(f'Bank account with id {id} does not exists!'), 404
    

@app.route('/account', methods=['GET'])
def get_bank_accounts():
    """Retrieves all bank accounts from the database.

    Returns:
        Various json strings and status codes based on different conditions.
        If successful, returns all accounts and 200 status code.
    """
    try:
        cur = get_db().cursor()
        cur.execute("SELECT * FROM Account")
        rows = cur.fetchall()
    except Exception as e:
        print(f"*** Error in routes/account/get_bank_accounts() ***: \n{e}")
        return jsonify("Server error: Cannot get bank accounts!"), 500
    else: 
        if rows:
            accounts = [dict(account) for account in rows]
            return json.dumps(accounts), 200
        return jsonify(f'There are no bank accounts in the database!'), 404


@app.route('/account/<id>', methods=['GET'])
def get_bank_account(id):   
    """Retrieves a bank account from the database.

    Returns:
        Various json strings and status codes based on different conditions.
        If successful, returns the account and 200 status code.
    """ 
    try:
        id = int(id)     
    except Exception as e:
        print(f"*** Error in routes/account/get_bank_account() ***: \n{e}")
        return jsonify("Server error: Specified ID could not be parsed to integer!"), 422
    else:
        try:
            cur = get_db().cursor()
            cur.execute("SELECT * FROM Account WHERE Id=?", (id,))
            row = cur.fetchone()
        except Exception as e:
            print(f"*** Error in routes/account/get_bank_account() ***: \n{e}")
            return jsonify("Server error: Cannot get the bank account!"), 500
        else:
            if row is None:
                return jsonify(f'Bank Account with id {id} does not exists'), 404
            account = dict(row)
            return json.dumps(account), 200


@app.route('/account/get-amount/<id>', methods=['GET'])
def get_amount_by_id(id):   
    """Retrieves a bank account from the database.
    Returns:
        Various json strings and status codes based on different conditions.
        If successful, returns the account and 200 status code.
    """ 
    try:
        id = int(id)     
    except Exception as e:
        return jsonify("Server error: Specified ID could not be parsed to integer!"), 422
    else:
        try:
            cur = get_db().cursor()
            cur.execute("SELECT UserId FROM BankUser WHERE UserId=?", (id,))
            userId = cur.fetchone()['UserId']       
            cur.execute("SELECT Amount FROM Account WHERE BankUserId=?", (userId,))          
            row = cur.fetchone()
            amount = dict(row)['Amount']
            
        except Exception as e:
            return jsonify("Server error: Cannot get the bank account!"), 500
        else:
            return jsonify({"amount": amount }), 200