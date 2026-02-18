import jwt
from config import Config
import datetime

def generate_jwt_token(user_id, email):
    now = datetime.datetime.now(datetime.timezone.utc)
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": now + datetime.timedelta(minutes=5)
    }

    token = jwt.encode(
        payload,
        Config.JWT_SECRET,
        algorithm="HS256"
    )

    return token

def verify_jwt_token(auth_header):
    if not auth_header:
        raise Exception("Authorization header is missing")
    
    try:
        token = auth_header.split(" ")[1]

        payload = jwt.decode(
            token,
            Config.JWT_SECRET,
            algorithms=["HS256"]
        )

        return payload
    
    except jwt.ExpiredSignatureError:
        raise Exception("Token has expired")
    
    except jwt.InvalidTokenError:
        raise Exception("Invalid token")
    