from flask import request, jsonify
from datetime import datetime
from nemidskat import app
from nemidskat.dbconfig import get_db
import requests
import json

@app.route('/pay-taxes', methods=['PUT'])
def pay_taxes():
    """Will pay user's (specified by userId) taxes for the particular 
    skat year (specified by skatYearId). This method firstly checks 
    if the taxes have been already paid. If not, it withdraws money 
    from the user's account to pay the taxes. 

    Returns:
        Various json strings and status codes based on different conditions.
        If the operation is successful, then in SkatUserYear, the IsPaid property
        for the specified user is turned to 1 (boolean - true) and return 200 status code.
    """
    try:
        user_id = int(request.json['userId'])
        # this might be chosen by the user on frontend
        skat_year_id = int(request.json['skatYearId'])
    except Exception as e:
        print(f"*** Error in routes/general/pay-taxes() ***: \n{e}")
        return jsonify("Check spelling and data types of request body elements!"), 400 
    else: 
        try:
            cur = get_db().cursor()
                        
            cur.execute('SELECT IsPaid, Amount FROM SkatUserYear WHERE UserId=? AND SkatYearId=?', 
                        (user_id, skat_year_id))
            record = cur.fetchone()
            
            if record is None:
                return jsonify(f'There is no skat record with the user ID: {user_id} ' +
                            f'and the skat year ID: {skat_year_id}'), 404
            
            # check if the user has already paid his taxes
            is_paid = dict(record)['IsPaid']
            if is_paid == 1:
                return jsonify("The user has already paid the taxes!"), 200
            
            response = requests.post('http://localhost:81/withdraw-money', json={
                "amount": dict(record)['Amount'],
                "userId": user_id})
            
            # if the amount was withdrawn, then turn IsPaid to 1 (true)
            if response.ok:
                cur.execute('UPDATE SkatUserYear SET IsPaid=? WHERE UserId=? AND SkatYearId=?', 
                            (1, user_id, skat_year_id))

                get_db().commit()
            # if the withdraw money event was not successful, then return status code and message
            # from its API to find out where the problem is
            else:
                return jsonify(json.loads(response.content)), response.status_code
            
        except Exception as e:
            print(f"*** Error in routes/general/pay_taxes() ***: \n{e}")
            return jsonify("Server error: unable to pay taxes!"), 500
        else:
            return jsonify("User's taxes have been successfully paid!"), 200
        