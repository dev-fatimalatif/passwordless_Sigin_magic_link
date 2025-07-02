import os
import json
import boto3
from botocore.exceptions import ClientError  # Make sure to import ClientError for error handling

# Get DynamoDB table name from environment variables
db_table = os.environ["DYNAMO_DB_TABLE_USERS"]
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(db_table)

def put_db_data(user_id, email):
    try:
        # Store data into DynamoDB
        db_response = table.put_item(
            Item={
                'userId': user_id,
                'email': email
            }
        )
        # Return success response
        return {
            'statusCode': 200,
            'body': json.dumps('User data successfully stored!')
        }
    except ClientError as e:
        # Handle DynamoDB Client errors
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error storing data: {e.response['Error']['Message']}")
        }
    except Exception as e:
        # Handle other exceptions
        return {
            'statusCode': 500,
            'body': json.dumps(f"An unexpected error occurred: {str(e)}")
        }

def lambda_handler(event, context):
    # Log the incoming event for debugging
    print("Received event:", json.dumps(event))

    # Extract user attributes from the event object
    user_id = event['request']['userAttributes']['sub']
    email = event['request']['userAttributes']['email']

    # Call the function to store the user data in DynamoDB
    db_response = put_db_data(user_id, email)
    
    # Log the database response (optional)
    print("DynamoDB Response:", db_response)

    # Just return the auto-confirm response for testing
    # event["response"] = {
    #     "db_response" : db_response
    # }
    return event
