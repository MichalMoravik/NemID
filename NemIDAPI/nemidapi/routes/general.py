from nemidapi import app


# # When receiving POST request, create nemId for the user
# @app.route('/generate-nemId', methods=['POST'])
# def generate_nemId():
#     try:
#         cpr = request.json['cpr']
#         nemId = generate_nem_ID_number(cpr)
#         return jsonify({"nemId": nemId}), 201

#     except Exception as e:
#         print(f"******* Error in {script_name} when generating nemId *******")
#         print(f"Error: {e}")
#         return jsonify({"server error": "cannot generate nemID"}), 500



    
    
# @app.route('/authenticate', methods=['POST'])
# def authenticate():
#     try:
#         # data taken from the request body
#         password = request.json['password']
#         nem_ID = request.json['nemID']

#         # opening the database connection
#         conn = create_connection(database)
#         with conn:
#             user_id = check_if_user_exits(conn, password, nem_ID)
#             if user_id is not None:
#                 # generate nemID auth code
#                 generated_code = random.randint(100000, 999999)
#                 # store authentication log in the database
#                 store_in_database(conn, user_id, generated_code)
#                 # return generated code
#                 return jsonify({"generatedCode": f"{generated_code}"}), 200
#             return jsonify({"authError": "forbidden access"}), 403
        
#     except Exception as e:
#         print(f"******* Error in {script_name} when authenticating user *******")
#         print(f"Error: {e}")
#         return jsonify({"server error": "cannot authenticate user"}), 500