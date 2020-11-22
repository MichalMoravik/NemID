from flask import request, jsonify
from datetime import datetime
# from __init__.py file import app - for routes (@app.route)
from nemidbank import app
from nemidbank.dbconfig import get_db
import json
import requests

@app.route('/add-deposit', methods=['POST'])
def add_deposit():
    try:
        amount = int(request.json['amount'])
        bank_user_id = int(request.json['bankUserId'])
        created_at = datetime.now().strftime("%B %d, %Y %I:%M%p")
        modified_at = datetime.now().strftime("%B %d, %Y %I:%M%p")
    except Exception as e:
        print(f"*** Error in routes/general/add_deposit() *** \n{e}")
        return jsonify("Check spelling and data types of request body elements!"), 400
    else:
        # amount cannot be null or negative
        if amount <= 0 or amount is None:
            return jsonify("The amount must be a positive number."), 422
        
        try:
            cur = get_db().cursor()
            
            # find out if the specified account exists and obtain current amount
            cur.execute(f"SELECT Amount FROM Account WHERE BankUserId=?", (bank_user_id,))
            record = cur.fetchone()
            if record is None:
                return jsonify(f'A bank user with id: {bank_user_id} does not have a bank account!'), 404
            old_amount = dict(record)['Amount']
            
            try:
                # send this amount to the interest rate function
                response = requests.post('http://localhost:7071/api/interestrate', json={"amount": amount})
                # getting back amount plus the interest
                amount = json.loads(response.content)['amountWithInterest']
            except Exception as e:
                print(f"*** Error in routes/general/add_deposit() *** \n{e}")
                return jsonify("Server error: Could not receive amount" \
                    "with interest from the 'interestrate' serverless function!"), 500
            else:
                # new amount is the old (current) amount on the account 
                # plus the new (deposited) amount plus the interest
                # and rounded to two decimal points
                new_amount = round(old_amount + amount, 2)

                # transaction - update account with a new amount and insert into deposit table a new record
                commands = [
                    ('UPDATE Account SET ModifiedAt=?, Amount=? WHERE BankUserId=?', (modified_at, new_amount, bank_user_id)),
                    ('INSERT INTO Deposit(BankUserId, CreatedAt, Amount) VALUES (?,?,?)', (bank_user_id, created_at, amount))]
                
                for command in commands:
                    cur.execute(command[0], command[1])
                    
                get_db().commit()
        except Exception as es:
            print(f"*** Error in routes/general/add_deposit() *** \n{es}")
            return jsonify("Server error: Could not successfully perform this operation. " \
                "Possible database problem"), 500
        else:
            return jsonify({"msg": "Operation successfully performed and recorded!", 
                            "newAmount": str(new_amount)}), 201


@app.route('/list-deposits/<id>', methods=['GET'])
def list_deposits(id):
    try:
        bank_user_id = int(id)
    except Exception as e:
        print(f"*** Error in routes/general/list_deposits() *** \n{e}")
        return jsonify("Check spelling and data types of request body elements!"), 400
    else:
        try:
            cur = get_db().cursor()
            cur.execute("SELECT * FROM Deposit WHERE BankUserId=?", (bank_user_id,))
            rows = cur.fetchall()
        except Exception as e:
            print(f"*** Error in routes/general/list_deposits() ***: \n{e}")
            return jsonify("Server error: Cannot retrieve deposits!"), 500
        else:
            if rows:
                deposits = [dict(deposit) for deposit in rows]
                return json.dumps(deposits), 200
            return jsonify(f'There are no deposits from the bank user with this id: {bank_user_id}!'), 404
        
        
@app.route('/create-loan', methods=['POST'])
def create_loan():
    try:
        loan_amount = int(request.json['loanAmount'])
        bank_user_id = int(request.json['bankUserId'])
        created_at = datetime.now().strftime("%B %d, %Y %I:%M%p")
        modified_at = datetime.now().strftime("%B %d, %Y %I:%M%p")
    except Exception as e:
        print(f"*** Error in routes/general/create_loan() *** \n{e}")
        return jsonify("Check spelling and data types of request body elements!"), 400
    else:
        try:
            cur = get_db().cursor()
                
            # find out if the specified account exists and obtain current amount
            cur.execute(f"SELECT Amount FROM Account WHERE BankUserId=?", (bank_user_id,))
            record = cur.fetchone()
            if record is None:
                return jsonify(f'A bank user with id: {bank_user_id} does not have a bank account!'), 404
            old_amount = dict(record)['Amount']
            
            try:
                # send the loan amount to the loan algorithm function
                response = requests.post('http://localhost:7071/api/loanalgorithm', 
                                        json={
                                            "amount": loan_amount,
                                            "accountAmount": old_amount
                                            })
            except Exception as e:
                print(f"*** Error in routes/general/create_loan() *** \n{e}")
                return jsonify("Server error: Could not receive a status code " \
                    "from the 'loanalgorithm' serverless function!"), 500
            else:
                if response.status_code != 200:
                    return jsonify("Error: The loan amount cannot be higher than 75% " \
                        "of current holdings!"), 403
                
                # new amount is the old (current) amount of money on the account plus the loan
                new_amount = old_amount + loan_amount
                    
                # transaction - update account with a new amount and insert into loan table a new record
                commands = [
                    ('UPDATE Account SET ModifiedAt=?, Amount=? WHERE BankUserId=?', 
                        (modified_at, new_amount, bank_user_id)),
                    ('INSERT INTO Loan(BankUserId, CreatedAt, ModifiedAt, Amount) VALUES (?,?,?,?)', 
                        (bank_user_id, created_at, modified_at, loan_amount))]
                
                for command in commands:
                    cur.execute(command[0], command[1])
                    
                get_db().commit()
        except Exception as es:
            print(f"*** Error in routes/general/create_loan() *** \n{es}")
            return jsonify("Server error: Could not successfully perform this operation. " \
                "Possible database problem"), 500
        else:
            return jsonify({"msg": "Operation successfully performed and recorded!", 
                            "newAmount": str(new_amount)}), 201