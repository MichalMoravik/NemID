from flask import request, jsonify
from datetime import datetime
from nemidskat import app
from nemidskat.dbconfig import get_db
import json
import requests


@app.route('/pay-taxes', methods=['POST'])
def pay_taxes():
    """
    The method has been started but not completele implemented - I didn't know how to reach out to the total amount that is in the user's bank account and I also
    didn't manage to call the Tax Calculator function and substract from the account.
    - The method should take a body with a UserId and the total amount of the user's bank account.
    - There should be an initial check if the user has paid taxes (check Amount/IsPaid from SkatUserYear)
    - The call to the Tax Calculator should be made, depending on its response the Amount and IsPaid in SkatUserYear should be updated
    - The call to the Bank API should be made to substract money from the account
    """
    try:
        bank_user_id = str(request.json['bankUserId'])
        amount = int(request.json['amount'])
    except Exception as e:
        print(f"*** Error in routes/general/pay-taxes() ***: \n{e}")
        return jsonify("Check spelling and data types of request body elements!"), 400 
    else: 
        try: 
            cur=get_db().cursor()
            cur.execute(f'SELECT Amount FROM SkatUserYear WHERE UserId=?', (bank_user_id,))
            amount=int(cur.fetchone()[0])
        except Exception as e:
            print(f"*** Error in routes/general/pay-taxes() ***: \n{e}")
            return jsonify("Server error: Cannot retrieve Amount!"), 500
        else:
            if amount > 0:
                try:
                    response = requests.post('http://localhost:7071/api/Skat_Tax_Calculator', json={"amount":amount})
                except Exception as e:
                    print(f"*** Error in routes/general/pay-taxes() *** \n{e}")
                    return jsonify("Server error: Could not receive a response from Tax Calculator!"), 500
                else:
                    try:
                        cur.execute(f'UPDATE SkatUserYear SET Amount = *not-implemented*, IsPaid = 1 WHERE UserId=?', (bank_user_id,))
                        get_db().commit()
                        return jsonify({"The operation was completed successfully and SkatUserYear was updated"}), 200
                    except Exception as e:
                        print(f"*** Error in routes/general/pay-taxes() ***: \n{e}")
                        return jsonify("Server error: Cannot retrieve Amount!"), 500
            else:
                return jsonify({"All the taxes have been paid"}), 201



                    
                    
                        
