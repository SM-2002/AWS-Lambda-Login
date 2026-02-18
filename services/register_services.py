from db.db_connection import get_connection
from services.otp_services import verify_otp_service
from utils.validater import validate_email, validate_phone, is_strong_password
import bcrypt
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def register_user_service(first_name, last_name, gender, email, password, phone_ccode_number):
    
    logger.info(f"Registering user with email: {email}")
    try:
        # validate email
        if not validate_email(email):
            return {
                "statusCode": 400,
                "error": "Invalid email format"
            }
        
        # validate phone
        if not validate_phone(phone_ccode_number):
            return {
                "statusCode": 400,
                "error": "Invalid phone format"
            }
        
        # validate strong password
        if not is_strong_password(password):
            return {
                "statusCode": 400,
                "error": "Password is weak, enter a strong password"
            }
        
        conn = get_connection()
        cur = conn.cursor()

        # check if user already exists in users table
        # sp_get_user_id()
        cur.callproc("sp_get_user_id", (email,))
        existing_user = None
        existing_user = cur.fetchone()

        if existing_user:
            logger.warning(f"User with email {email} already exists")
            cur.close()
            conn.close()
            return {
                "statusCode": 400,
                "error": "User with this email already exists"
            }
        
        # check if exists in pending users table
        # sp_get_pending_user_id()
        cur.callproc("sp_get_pending_user_id", (email,))
        pending_user = None
        pending_user = cur.fetchone()


        if pending_user:
            logger.warning(f"User with email {email} already exists in pending users")
            cur.close()
            conn.close()
            return {
                "statusCode": 400,
                "error": "User with this email already exists"
            }

        # hash password
        hashed_password = bcrypt.hashpw(
                password.encode('utf-8'),
                bcrypt.gensalt()
            ).decode('utf-8')


        # insert into pending users table
        # sp_insert_into_pending_users()
        cur.callproc("sp_insert_into_pending_users", (
            first_name,
            last_name,
            gender,
            email,
            hashed_password,
            phone_ccode_number
        ))

        conn.commit()

        # get pending user id
        # sp_get_pending_user_id()
        cur.callproc("sp_get_pending_user_id", (email,))
        pending_user_row = None
        pending_user_row = cur.fetchone()
        pending_user_id = pending_user_row['id']

        cur.close()
        conn.close()
        logger.info(f"Inserted user with email {email} into pending_users table")


        logger.info(f"Successfully registered user with email: {email}")
        return {
            "statusCode": 200,
            "data": {
                "pending_user_id" : pending_user_id,
                "message": "Continue Verification"
            }
        }
    
    except Exception as e:
        logger.error(f"Error occured in registering the user with email {email}: {str(e)}")

        return {
            "statusCode": 500,
            "error": "An error occurred while registering the user"
        }
    
def verify_otp_and_create_user_service(pending_user_id, otp_code):
    try:
        conn = get_connection()
        cur = conn.cursor()

        # get phone number from pending_users table
        # sp_get_phone_ccode_number_from_pending_users()
        cur.callproc("sp_get_phone_ccode_number_from_pending_users", (pending_user_id,))
        phone_row = None
        phone_row = cur.fetchone()
        
        phone = phone_row['phone_ccode_number']

        # verify otp 
        verification_result = verify_otp_service(phone, otp_code)

        # verification not approved
        if verification_result.get('statusCode') != 200:
            return verification_result

        # verification approved
        # get pending user details using pending_user id
        # sp_get_pending_user_details()
        cur.callproc("sp_get_pending_user_details", (pending_user_id,))
        pending_user = None
        pending_user = cur.fetchone()

        if not pending_user:
            logger.warning(f"No pending user found with ID: {pending_user_id}")
            cur.close()
            conn.close()
            return {
                "statusCode": 400,
                "error": "No pending user found with this ID"
            }

        # insert pending user details into users table
        # sp_insert_into_users()
        cur.callproc("sp_insert_into_users", (
            pending_user['first_name'],
            pending_user['last_name'],
            pending_user['gender'],
            pending_user['email'],
            pending_user['password'],
            pending_user['phone_ccode_number']
        ))
        
        # get user id of recently created user
        # sp_get_user_id()
        cur.callproc("sp_get_user_id", (pending_user['email'],))
        user_row = None
        user_row = cur.fetchone()
        user_id = user_row['id']

        # delete it from pending user
        # sp_delete_from_pending_users()
        cur.callproc("sp_delete_from_pending_users", (pending_user_id,))

        conn.commit()
        cur.close()
        conn.close()

        logger.info(f"User with email {pending_user['email']} created successfully after OTP verification")

        return {
            "statusCode": 200,
            "data": {
                "message": "User created successfully",
                "User ID": user_id
            }
        }
    
    except Exception as e:
        logger.error(f"Error creating user with email {pending_user['email']} after OTP verification: {str(e)}")

        return {
            "statusCode": 500,
            "error": "An error occurred while creating the user after OTP verification"
        }