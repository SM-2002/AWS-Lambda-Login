from db.db_connection import get_connection
from utils.validater import validate_email
from utils.jwt_helper import generate_jwt_token
import json
import bcrypt
import logging


logger = logging.getLogger()
logger.setLevel(logging.INFO)


def login_user(email, password):
    logger.info(f"Attempting login for email: {email}")
    try:
        if not validate_email(email):
            return {"error": "Invalid email format", "statusCode": 400}
        
        conn = get_connection()
        cur = conn.cursor()

        # sp_check_login_get_user_credentials(email)
        cur.callproc("sp_check_login_get_user_credentials", (email,))
        
        user = cur.fetchone()

        cur.close()
        conn.close()

        # check if user exists
        if not user:
            logger.warning(f"User not found for email: {email}")
            return {
                "statusCode": 401,
                "error": "Invalid email"
            }
        
        logger.info(f"User found: {user['email']}, checking password")

        # check if user is active
        if not user['status']:
            logger.warning(f"User account is inactive for email: {email}")
            return {
                "statusCode": 403,
                "error": "User account is inactive"
            }
        
        # check password
        stored_password = user['password']
        # convert to bytes only if its a string
        if isinstance(stored_password, str):
            stored_password = stored_password.encode('utf-8')
            
        if not bcrypt.checkpw(password.encode('utf-8'), stored_password):
            logger.warning(f"Password mismatch for email: {email}")
            return {
                "statusCode": 401,
                "error": "Password mismatch"
            }
       
        logger.info(f"User authenticated successfully: {email}")

        token = generate_jwt_token(user['id'], user['email'])
        logger.info(f"JWT token generated for email: {email}")

        return {
            "statusCode": 200,
            "body" : {
                "message": "Login successful",
                "token": token,
            } 
        }
    
    except Exception as e:
        logger.error(f"Error during login for email: {email} - {str(e)}")
        return {
            "statusCode": 500,
            "error": "An error occurred during login"
        }
    
def get_users(limit, offset):
    try:
        conn = get_connection()
        cur = conn.cursor()

        # # sp_get_users()
        # cur.callproc("sp_get_users")
        # users = cur.fetchall()

        # sp_pagination_get_users(limit, offset)
        cur.callproc("sp_pagination_get_users", (limit, offset))
        users = cur.fetchall()

        cur.close()
        conn.close()

        return users
    
    except Exception as e:
        logger.error(f"Error fetching users: {str(e)}")
        return {
            "statusCode": 500,
            "error": "An error occurred while fetching users"
        }

        
