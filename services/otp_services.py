import os
import logging
from twilio.rest import Client
from db.db_connection import get_connection

logger = logging.getLogger()
logger.setLevel(logging.INFO)

client = Client(
    os.environ.get('TWILIO_ACCOUNT_SID'),
    os.environ.get('TWILIO_AUTH_TOKEN')
)

VERIFY_SERVICE_SID = os.environ['TWILIO_VERIFY_SERVICE_SID']

def send_otp_service(pending_user_id):
    logger.info(f"Trying to send otp to phone for pending user with id: {pending_user_id}")

    try:
        conn = get_connection()
        cur = conn.cursor()

        # check if user exists in pending_user table
        # sp_user_in_pending_users()
        cur.callproc("sp_user_in_pending_users", (pending_user_id,))
        exists = None
        exists = cur.fetchone()

        if not exists:
            cur.close()
            conn.close()
            logger.warning(f"ERROR: User not found in pending users table")
            return {
                "statusCode": 404,
                "data": {
                    "message": "user not found in pending users list"
                }
            }
        
        # get phone number from pending_users table
        # sp_get_phone_ccode_number_from_pending_users()
        cur.callproc("sp_get_phone_ccode_number_from_pending_users", (pending_user_id,))
        pending_user_row = None
        pending_user_row = cur.fetchone()
        phone = pending_user_row['phone_ccode_number']
        
        # send otp to phone number
        verification = client.verify.services(VERIFY_SERVICE_SID).verifications.create(to=phone, channel='sms')

        logger.info(f"OTP sent successfully to {phone}")

        # update otp request time in pending_users table
        # sp_update_otp_requested_time_in_pending_users()
        cur.callproc("sp_update_otp_requested_time_in_pending_users", (pending_user_id,))

        conn.commit()
        cur.close()
        conn.close()

        logger.info(f"OTP request time for phone: {phone} updated in pending users table")

        return {
            "statusCode": verification.status,
            "data": {
                "message": f"OTP sent to {phone}"
            }
        }
    
    except Exception as e:
        logger.error(f"Error sending OTP: {str(e)}")
        return {
            "statusCode": 500,
            "error": "Failed to send OTP"
        }
    
def verify_otp_service(phone, otp_code):
    try:
        logger.info(f"Verifying OTP for phone: {phone}")

        verification_check = client.verify.services(VERIFY_SERVICE_SID).verification_checks.create(to=phone, code=otp_code)

        if verification_check.status != "approved":
            logger.warning(f"OTP verification failed for phone: {phone}")
            return {
                "statusCode": 401,
                "error": "Invalid OTP"
            }
        
        logger.info(f"OTP verified successfully for phone: {phone}")
        return {
            "statusCode": 200,
            "data": {
                "message": "OTP verified successfully"
            }
        }

    except Exception as e:
        logger.error(f"Error verifying OTP for {phone}: {str(e)}")
        return {
            "statusCode": 500,
            "error": "OTP verification failed"
        }
    

