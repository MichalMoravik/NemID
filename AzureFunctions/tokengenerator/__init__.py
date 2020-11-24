import logging
import azure.functions as func
from datetime import datetime, timedelta
import json

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Token Generator (tokengenerator) - a new request has been registered!')

    try:
        nem_id = str(req.get_json().get('nemId'))
    except Exception as e:
        logging.exception(f"*** Error in tokengenerator (azure serverless function) *** \n{e}")
        return func.HttpResponse(
                "Check spelling and data types of request body elements!",
                status_code=400
            )
    else:
        try:
            generated_token = generate_token(nem_id)
            return func.HttpResponse(json.dumps({"token": generated_token}), status_code=200)
        except Exception as e:
            return func.HttpResponse(json.dumps({
                "msg": "Server error: Could not generate JWT token!"
                }), status_code=500)


def generate_token(nem_id):
    payload = {
        "nemId": nem_id,
        "permissions": "basic-user",
        "iat": datetime.now(),
        "exp": datetime.now() + timedelta(minutes=20)
    }

    token = jwt.encode(payload, "Bezpecnostny kluc", algorithm="HS256")
    return token