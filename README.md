# AWS Lambda Login Service

A lightweight Python-based login and authentication microservice designed to run on AWS Lambda. It handles user registration, login, OTP verification, JWT token generation, and integrates with third-party services like Twilio and MySQL.

## 🚀 Features

- **User Authentication** – Register and authenticate users.
- **OTP Support** – One-time password generation and validation.
- **JWT Tokens** – Secure access tokens for session management.
- **Modular Architecture** – Clear separation of routes, services, utilities, and configuration.
- **AWS Lambda Ready** – Can be deployed via AWS SAM/CloudFormation using `template.yaml`.
- **Third-party Integrations** – Twilio for SMS OTP, PyMySQL for database access.

## 📁 Project Structure

```
lambda-login/
├── app.py                 # Lambda entry point
├── config.py              # Configuration and environment loading
├── template.yaml          # AWS SAM template
├── routes/                # API route definitions
│   └── auth_routes.py
├── services/              # Business logic
│   ├── auth_services.py
│   ├── otp_services.py
│   └── register_services.py
├── utils/                 # Helpers and utilities
│   ├── jwt_helper.py
│   ├── response.py
│   ├── twilio_helper.py
│   └── validater.py
├── db/                    # Database connection logic
│   └── db_connection.py
├── events/                # Sample event payloads for testing
├── requirements.txt       # Python dependencies
└── readme.md
``` 

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/lambda-login.git
   cd lambda-login
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv .venv
   source .venv/Scripts/activate  # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## ⚙️ Configuration

Configuration values are managed in `config.py`, which reads from environment variables. Key settings include:

- `DB_HOST`, `DB_USER`, `DB_PASS`, `DB_NAME` – MySQL connection parameters
- `JWT_SECRET`, `JWT_ALGORITHM` – JWT signing
- `TWILIO_SID`, `TWILIO_TOKEN`, `TWILIO_FROM` – Twilio credentials

Set them in your local environment or pass through Lambda environment variables.

## 🧪 Testing Locally

You can invoke functions locally using AWS SAM CLI or simple Python scripts. Example using sample event:

```bash
python - <<'PYCODE'
from app import lambda_handler
import json

event = json.load(open('events/login_user1.json'))
print(lambda_handler(event, None))
PYCODE
```

## 🚀 Deployment

Deploy with AWS SAM:

```bash
sam build
sam deploy --guided
```

This will create an API Gateway, Lambda function, and required IAM roles.

## 🧩 Adding Routes and Services

1. **Define a new route** in `routes/auth_routes.py`.
2. **Implement business logic** in the appropriate service under `services/`.
3. **Use helpers** from `utils/` for common tasks like JWT creation or responses.

## 📦 Dependencies

See `requirements.txt` for full list. Currently includes:

- `PyJWT`
- `pymysql`
- `bcrypt`
- `twilio`
