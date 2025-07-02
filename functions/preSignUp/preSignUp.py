import json

def lambda_handler(event, context):
    # Log the event object for debugging
    print(f"Received event: {json.dumps(event)}")

    # Custom validation logic (example: block a specific domain)
    email = event['request']['userAttributes']['email']
    if email.endswith('@example.com'):
        raise Exception('This email domain is not allowed for sign-up.')

    # Optionally modify attributes or auto-confirm
    event['response']['autoConfirmUser'] = True  # Auto-confirm the user after validation

    # Returning the event to proceed with signup
    return event