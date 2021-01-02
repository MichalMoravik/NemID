from flask import request, jsonify
from datetime import datetime
from nemidskat import app
from nemidskat.dbconfig import get_db
import requests


@app.route('/pay-taxes', methods=['POST'])
def pay_taxes():
    """
        1. takes userId and total amount of the user's bank account (using this userId)
        2. check if the user already paid his taxes (IsPaid) 
        3. it will see the amount of money a user has on his account
        4. it will then send request to the function and calculate how much taxes he has to pay
        5. after that it takes this calculated taxes from his account and set the "IsPaid" to 1.
        6. the call to bank API should be made to substract money from the account
        
        what if we do it while creating a new skat year, just to look to bank account and count the amount they have to pay 
    """
    try:
        user_id = int(request.json['userId'])
        #amount = int(request.json['amount'])
        r = requests.get(f'http://bank:81/get-amount/{user_id}')
        data = r.json()
        bank_amount = data['amount']
    except Exception as e:
        print(f"*** Error in routes/general/pay-taxes() ***: \n{e}")
        return jsonify("Check spelling and data types of request body elements!"), 400 
    else: 
        try: 
            cur=get_db().cursor()
            cur.execute(f'SELECT Amount FROM SkatUserYear WHERE UserId=?', (user_id,))
            skat_amount = int(cur.fetchone()[0])
            print(skat_amount)
        except Exception as e:
            print(f"*** Error in routes/general/pay-taxes() ***: \n{e}")
            return jsonify("Server error: Cannot retrieve Amount!"), 500
        else:
            if skat_amount > 0:
                try:
                    response = requests.post('http://functions:80/api/Skat_Tax_Calculator', json={"money":bank_amount})
                    data=response.json()
                    tax_money=data['tax_money']
                except Exception as e:
                    print(f"*** Error in routes/general/pay-taxes() *** \n{e}")
                    return jsonify("Server error: Could not receive a response from Tax Calculator!"), 500
                else:
                    try:
                        #IMPLEMENT PAY TAXES
                        response = requests.post('http://bank:81/withdraw-money', json={"amount":skat_amount, "userId":user_id})
                        cur.execute(f'UPDATE SkatUserYear SET Amount = 0, IsPaid = 1 WHERE UserId=?', (user_id,))
                        get_db().commit()
                        return jsonify({"The operation was completed successfully and SkatUserYear was updated"}), 200
                    except Exception as e:
                        print(f"*** Error in routes/general/pay-taxes() ***: \n{e}")
                        return jsonify("Server error: Cannot retrieve Amount!"), 500
            else:
                return jsonify("All the taxes have been paid"), 201



                    
                    
                        
