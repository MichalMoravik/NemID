import logging
import azure.functions as func
import json

def main(req: func.HttpRequest) -> func.HttpResponse:  
    try: 
        req_body = req.get_json()
    except ValueError as e:
        return func.HttpResponse(body=f"*** Could not get body of the request! *** \n{e}", status_code=404)
    else:
        deposited_amount = req_body.get('amount')
        interest_rate = 0.02
        # returned amount is a deposited amount + 2% (interest rate) from the deposited amount
        new_amount = deposited_amount + deposited_amount * interest_rate
        return func.HttpResponse(body=json.dumps({"amountWithInterestRate": new_amount}))