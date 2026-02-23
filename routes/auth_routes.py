import json
from services.auth_services import login_user, get_users
from utils.response import success_response, error_response
from utils.jwt_helper import verify_jwt_token
from services.otp_services import send_otp_service
from services.register_services import register_user_service, verify_otp_and_create_user_service

def login_route(event):
    try:
        body = json.loads(event['body'])
        data = login_user(body['email'], body['password'])
        return success_response(data)
    
    except Exception as e:
        return error_response(str(e), 500)

def get_users_route(event):
    try:
        auth_header = event['headers'].get('Authorization')

        verify_jwt_token(auth_header)

        # get page, limit, offset
        query_params = event.get("queryStringParameters") or {}

        page = int(query_params.get("page", 1))
        limit = int(query_params.get("limit", 10))

        offset = (page - 1) * limit

        users = get_users(limit, offset)

        return success_response(users)
    
    except Exception as e:
        return error_response(str(e), 401)
    
def send_otp_route(event):
    try:
        body = json.loads(event['body'])
        pending_user_id = body['id']

        if not pending_user_id:
            return error_response("Pending User's ID is required", 400)
        
        result = send_otp_service(pending_user_id)

        return success_response(result)
    
    except Exception as e:
        return error_response(str(e), 500)
    
def verify_otp_route(event):
    try:
        body = json.loads(event['body'])
        pending_user_id = body['id']
        otp_code = body['otp']

        result = verify_otp_and_create_user_service(pending_user_id, otp_code)

        return success_response(result)
    
    except Exception as e:
        return error_response(str(e), 500)
    

def register_route(event):
    try:
        body = json.loads(event['body'])

        required_fields = [
            'first_name',
            'last_name',
            'gender',
            'email',
            'password',
            'phone_ccode_number'
        ]

        # check missing fields
        for field in required_fields:
            if field not in body:
                return error_response(f"{field} is required", 400)
            
        response = register_user_service(
            body.get('first_name'),
            body.get('last_name'),
            body.get('gender'),
            body.get('email'),
            body.get('password'),
            body.get('phone_ccode_number')
        )

        if response.get('statusCode') != 200:
            return error_response(response['error'], response['statusCode'])
        

        return success_response(response['data'])
    
    except Exception as e:
        return error_response(str(e), 500)