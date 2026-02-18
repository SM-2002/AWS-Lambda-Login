# import json
# import pymysql
# import bcrypt
# import jwt
# import logging


# logger = logging.getLogger()
# logger.setLevel(logging.INFO)




# def lambda_handler(event, context):
#     logger.info("Lambda invoked with event: %s", json.dumps(event))
#     # logger.info("Context: %s", str(context))

#     try:
#         logger.info(f"Parsing request body: {event}")
#         body = json.loads(event['body'])
#         email = body.get('email')
#         password = body.get('password')

#         if not email or not password:
#             logger.warning("Missing email or password in request body")
#             return {
#                 "statusCode": 400,
#                 "body": json.dumps({"error": "Email and password are required"})
#             }
        
#         # DB Query
#         conn = get_connection()
#         cur = conn.cursor()

#         sql = """
#             SELECT id, email, password, status 
#             FROM users
#             WHERE email = %s
#         """
#         cur.execute(sql, (email,))

#         user = cur.fetchone()

#         cur.close()
#         conn.close()

#         if not user:
#             logger.warning("User not found for email: %s", email)
#             return {
#                 "statusCode": 401,
#                 "body": json.dumps({"error": "Invalid credentials"})
#             }   
        
#         if not user['status']:
#             logger.warning("Invalid status for user: %s", email)
#             return {
#                 "statusCode": 403,
#                 "body": json.dumps({"error": "User account is inactive"})
#             } 
        
#         # Password verification
#         if not bcrypt.checkpw(
#             password.encode('utf-8'),
#             user['password'].encode('utf-8')
#         ):
#             logger.warning("Password mismatch for user: %s", email)
#             return {
#                 "statusCode": 401,
#                 "body": json.dumps({"error": "Invalid credentials"})
#             }
        
#         # JWT token generation
#         # jwt payload(user data) -> jwt secret(signing key) -> algorithm(HS256) encryption method -> token
#         token = jwt.encode(
#             {"user_id": user['id'], "email": user['email']},
#             JWT_SECRET,
#             algorithm="HS256"
#         )

#         logger.info("User authenticated successfully: %s", email)

#         return {
#             "statusCode": 200,
#             "body": json.dumps(
#                 {
#                     "message": "Login successful",
#                     "token": token
#                 }
#             )
#         }

#     except Exception as e:
#         logger.error("Error during login process: %s", str(e))
#         return {
#             "statusCode": 500,
#             "body": json.dumps({"error": "Internal server error"})
#         }


import json
import logging
from routes.auth_routes import get_users_route, login_route, send_otp_route, verify_otp_route, register_route
from dotenv import load_dotenv

logger = logging.getLogger()
logger.setLevel(logging.INFO)

load_dotenv()

def lambda_handler(event, context):

    logger.info("Lambda invoked with event: %s", json.dumps(event))

    method = event.get('httpMethod')
    path = event.get('pathParameters', {}).get('proxy', '')

    logger.info("Method=%s Path=%s", method, path)

    if path == 'login' and method == 'POST':
        return login_route(event)
    
    if path == 'users' and method == 'GET':
        return get_users_route(event)
    
    if path == 'register' and method == 'POST':
        return register_route(event)
    
    if path == 'register/send-otp' and method == 'POST':
        return send_otp_route(event)
    
    if path == 'register/verify-otp' and method == 'POST':
        return verify_otp_route(event)
    
    return {
        "statusCode": 404,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps({
            "error": "Route not found"
        })
    }

    