from flask import request, jsonify
# from __init__.py file import app - for routes (@app.route)
from nemidapi import app
from nemidapi.models.user import *
from nemidapi.models.gender import *
import random
from datetime import datetime


# HELPERS
def generate_nem_ID_number(cpr: str):
    """will generate nemID number in form of: {random 5 digits}-{last four digits of CPR}

    Args:
        cpr (str): cpr in a string form

    Returns:
        str: nem id number
    """
    last_four_digits = cpr[-4:]
    random_five_digits = random.randint(10000, 99999)
    return f'{random_five_digits}-{last_four_digits}'


@app.route('/user', methods=['POST'])
def create_user():
    email = request.json['email']
    cpr = request.json['cpr']
    created_at = datetime.now().strftime("%B %d, %Y %I:%M%p")
    modified_at = datetime.now().strftime("%B %d, %Y %I:%M%p")
    gender_id = request.json['genderId']
    nem_id = generate_nem_ID_number(cpr)
    
    try:
        gender = Gender.query.filter_by(Id=gender_id).first()
        new_user = User(str(email), str(nem_id), str(cpr), str(created_at), str(modified_at), int(gender_id), gender)
        db.session.add(new_user)
        db.session.commit()

    except Exception as e:
        # print(f"******* Error in routes/customers.py: add_customer() *******")
        print(f"Error: {e}")
        return jsonify("Server error: unable to register user. See console for more info."), 500
    else:
        return user_schema.jsonify(new_user)


# @app.route('/customer', methods=['GET'])
# def get_customers():
#     try:
#         all_customers = Customer.query.all()
#         result = customers_schema.dump(all_customers)
#         return jsonify(result)
#     except Exception as e:
#         print(f"******* Error in routes/customers.py: get_customers() *******")
#         print(f"Error: {e}")
#         return jsonify("Cannot get customers!"), 500


# @app.route('/customer/<id>', methods=['GET'])
# def get_customer(id):
#     try:
#         customer = Customer.query.get(id)
#         return customer_schema.jsonify(customer)
#     except Exception as e:
#         print(f"******* Error in routes/customers.py: get_customer(id) *******")
#         print(f"Error: {e}")
#         return jsonify("Cannot get customer!"), 500


# @app.route('/customer/<id>', methods=['PUT'])
# def update_customer(id):
#     try:
#         first_name = request.json['first_name']
#         last_name = request.json['last_name']
#         email = request.json['email']

#         customer = Customer.query.get(id)
#         customer.first_name = first_name
#         customer.last_name = last_name
#         customer.email = email

#         db.session.commit()

#         return customer_schema.jsonify(customer)
#     except Exception as e:
#         print(f"******* Error in routes/customers.py: update_customer(id) *******")
#         print(f"Error: {e}")
#         return jsonify("Cannot update customer!"), 500


# @app.route('/customer/<id>', methods=['DELETE'])
# def delete_customer(id):
#     try:
#         customer = Customer.query.get(id)
#         db.session.delete(customer)
#         db.session.commit()

#         return customer_schema.jsonify(customer)
#     except Exception as e:
#         print(f"******* Error in routes/customers.py: delete_customer(id) *******")
#         print(f"Error: {e}")
#         return jsonify("Cannot delete customer!"), 500



