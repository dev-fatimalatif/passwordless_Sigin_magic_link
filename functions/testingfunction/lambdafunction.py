
import boto3
import os

# Initialize the Cognito client
cognito_client = boto3.client("cognito-idp", region_name="us-west-1")

# Environment variables
USER_POOL_CLIENT_ID = os.environ.get("USER_POOL_CLIENT_ID", "2o5j32tkqhojtdqsa84fut1s3")

def initiate_auth(email):
    """
    Initiate the custom auth flow for passwordless authentication.
    """
    try:
        response = cognito_client.initiate_auth(
            ClientId=USER_POOL_CLIENT_ID,
            AuthFlow="CUSTOM_AUTH",
            AuthParameters={
                "USERNAME": email
            }
        )
        # print("InitiateAuth Response:", response)
        return response
    except Exception as e:
        print(f"Error initiating auth: {e}")
        raise

def verify_magic_link(username,magic_token, session_token):
    """
    Verify the magic link by responding to the auth challenge.
    """
    if not magic_token:
        raise ValueError("Magic token is missing.")
    if not session_token:
        raise ValueError("Session token is missing.")

    try:
        response = cognito_client.respond_to_auth_challenge(
            ClientId=USER_POOL_CLIENT_ID,
            ChallengeName='CUSTOM_CHALLENGE',
            Session=session_token,
            ChallengeResponses={
                'USERNAME': username,
                'ANSWER': magic_token
            }
        )
        # print("VerifyMagicLink Response:", response)
        return response
    except Exception as e:
        print(f"Error verifying magic link: {e}")
        raise

def lambda_handler(event, context):
    """
    Lambda handler function for passwordless authentication.
    """
    try:
        if event["method"].lower() == "passwordless":
            email = event["email"]
            response = initiate_auth(email)

            # Extract and validate token and session
            session_token = response.get("Session")
            encoded_token = response["ChallengeParameters"].get("token")

            if not encoded_token:
                raise ValueError("Token not found in ChallengeParameters")
            if not session_token:
                raise ValueError("Session token missing in response")

            # Respond to the challenge
            # response = verify_magic_link(email, encoded_token, session_token)
            return {
                "statusCode": 200,
                # "body": response
            }
    except Exception as e:
        print(f"Error: {e}")
        return {
            "statusCode": 500,
            "body": str(e)
        }

