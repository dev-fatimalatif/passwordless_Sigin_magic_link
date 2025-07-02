import json
from datetime import datetime
import base64
def lambda_handler(event, context):
    print("VerifyAuthChallengeResponse event:", json.dumps(event, indent=2))

    expected_token = event["request"]["privateChallengeParameters"].get("token")
    provided_token = event["request"].get("challengeAnswer")

    if not expected_token or not provided_token:
        event["response"]["answerCorrect"] = False
    else:
        event["response"]["answerCorrect"] = (expected_token == provided_token)

    return event
