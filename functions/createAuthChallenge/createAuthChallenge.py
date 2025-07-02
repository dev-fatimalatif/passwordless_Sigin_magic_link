import json
import os
import boto3
import hmac
import hashlib
import time
import base64
import uuid
from botocore.exceptions import ClientError

# Environment variables
SES_FROM_ADDRESS = os.environ.get("SES_FROM_ADDRESS", "example@gmail.com")  # Change to your sender email
BASE_URL = os.environ.get("BASE_URL", "https://d84l1xxxxkdic.cloudfront.net")  # Update with your base URL
TIMEOUT_MINS = int(os.environ.get("TIMEOUT_MINS", 15))  # Expiration time in minutes
SECRET_KEY = os.environ.get("SECRET_KEY", "your-secure-secret-key")  # Replace with a secure secret key

# Initialize the SES client
ses = boto3.client("ses")

def generate_magic_token(email):
    """
    Generate a signed magic token and a magic link.
    """
    expiration_time = int(time.time()) + (TIMEOUT_MINS * 60)  # Expiry timestamp
    unique_id = str(uuid.uuid4())  # Unique token identifier
    token_data = f"{email}|{unique_id}|{expiration_time}"
    
    # Sign the token with HMAC-SHA256
    signature = hmac.new(
        SECRET_KEY.encode("utf-8"),
        token_data.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()
    
    # Combine token data with the signature
    token = f"{token_data}|{signature}"
    
    # Encode the token for URL safety
    encoded_token = base64.urlsafe_b64encode(token.encode()).decode()
    
    # Construct the magic link
    magic_link = f"{BASE_URL}?token={encoded_token}"
    return magic_link, encoded_token, expiration_time

def send_email(email, magic_link):
    """
    Send the magic link to the provided email address using SES.
    """
    try:
        response = ses.send_email(
            Source=SES_FROM_ADDRESS,
            Destination={
                "ToAddresses": [email]
            },
            Message={
                "Subject": {
                    "Data": "Your one-time sign-in link",
                    "Charset": "UTF-8"
                },
                "Body": {
                    "Html": {
                        "Data": f"""
                        <html>
                        <body>
                            <p>Your one-time sign-in link (valid for {TIMEOUT_MINS} minutes):</p>
                            <a href="{magic_link}">{magic_link}</a>
                        </body>
                        </html>
                        """,
                        "Charset": "UTF-8"
                    },
                    "Text": {
                        "Data": f"Your one-time sign-in link (valid for {TIMEOUT_MINS} minutes): {magic_link}",
                        "Charset": "UTF-8"
                    }
                }
            }
        )
        print(f"Email sent successfully to {email}. SES Response: {response}")
    except ClientError as e:
        print(f"Failed to send email to {email}. Error: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error while sending email: {e}")
        raise

def lambda_handler(event, context):
    """
    CreateAuthChallenge Lambda handler for AWS Cognito custom auth flow.
    """
    try:
        # Log the incoming event for debugging
        print("Received event:", json.dumps(event, indent=2))
        
        # Extract the user's email address
        email = event["request"]["userAttributes"].get("email")
        if not email:
            raise ValueError("Email address not found in user attributes")
        
        # Generate the magic token and link
        magic_link, token, expiration_time = generate_magic_token(email)
        print(f"Generated magic link: {magic_link}")
        print(f"Generated token: {token}")
        
        # Send the magic link via email
        send_email(email, magic_link)
        print(f"Magic link sent to {email}")
        
        # Set the public and private challenge parameters
        event["response"]["publicChallengeParameters"] = {
            "email": email,
            "token": token
        }
        event["response"]["privateChallengeParameters"] = {
            "token": token,
            "expiration_time": expiration_time
        }
        event["response"]["challengeMetadata"] = "MAGIC_LINK_SENT"
        
        # Log the response for debugging
        print("Response prepared for Cognito:", json.dumps(event, indent=2))
        return event
    
    except Exception as e:
        print(f"Error in CreateAuthChallenge handler: {str(e)}")
        raise
