import logging
import azure.functions as func
import json

def main(req: func.HttpRequest) -> func.HttpResponse:  
    try: 
        # amount of money a user want's to borrow
        loan_amount = req.get_json().get('amount')
        # amount of money a user currently has on his account
        account_amount = req.get_json().get('accountAmount')
    except ValueError as e:
        return func.HttpResponse(body=f"*** Body of the request is not valid! *** \n{e}", status_code=404)
    else:
        # the amount of money a user wants to borrow must be less than 75% of user's current assets
        benchmark = account_amount * 0.75
        if loan_amount >= benchmark:
            return func.HttpResponse(status_code=403) 
        return func.HttpResponse(status_code=200)