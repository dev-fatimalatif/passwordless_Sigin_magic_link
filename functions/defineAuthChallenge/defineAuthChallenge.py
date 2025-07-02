import json
def lambda_handler(event, context):
    print("DefineAuthChallenge event:", json.dumps(event, indent=2))

    # 1. If the user does not exist
    if event["request"].get("userNotFound"):
        event["response"]["issueTokens"] = False
        event["response"]["failAuthentication"] = True
        return event

    # 2. If challenge was passed successfully
    if event["request"].get("session") and event["request"]["session"][-1]["challengeResult"]:
        event["response"]["issueTokens"] = True
        event["response"]["failAuthentication"] = False
        return event

    # 3. Otherwise, continue challenge
    event["response"]["issueTokens"] = False
    event["response"]["failAuthentication"] = False
    event["response"]["challengeName"] = "CUSTOM_CHALLENGE"

    return event
