import logging
import azure.functions as func
import json

def main(req: func.HttpRequest) -> func.HttpResponse:  
    try: 
        deposited_amount = req.get_json().get('amount')
    except ValueError as e:
        return func.HttpResponse(body=f"*** Body of the request is not valid! *** \n{e}", status_code=404)
    else:
        interest_rate = 0.02
        # returned amount is a deposited amount + 2% (interest rate) from the deposited amount
        new_amount = deposited_amount + deposited_amount * interest_rate
        return func.HttpResponse(body=json.dumps({"amountWithInterest": new_amount}), status_code=200)