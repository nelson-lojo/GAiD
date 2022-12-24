import json
import PyNaCl

def lambda_handler(event: Dict, context):
    
    valid, error = validateType(event)
    if not valid:
        return error

    return route(event)

def validateType(data: Dict) -> Tuple[bool, Dict]:
    request_type: int = data.get('type', None)

    if request_type is None:
        return False, {
            "statusCode" : 400,
            "body" : "Request type not specified"
        }
    
    request_type = int(request_type)

    if request_type > 12:
        return False, {
            "statusCode" : 406,
            "body" : "No Interaction with this type found"
        }
    
    return True, {}

def route(interaction: Dict):
    if interaction['type'] == 1:
        return {
            "statusCode" : 200,

        }





# "hey google ..."
# play music in a voice chat
# black scholes model

# lambda response
{
  "statusCode": 200,
  "body": {
    "event": "{\"key1\": \"value1\", \"key2\": \"value2\", \"key3\": \"value3\"}",
    "context": {
      "type": "<class 'awslambdaric.lambda_context.LambdaContext'>",
      "data": "LambdaContext([aws_request_id=6d1fe367-07fe-4b7d-9f2d-9172de87941b,log_group_name=/aws/lambda/test,log_stream_name=2022/12/24/[$LATEST]0534b686b61e4775917946f221a5d75a,function_name=test,memory_limit_in_mb=128,function_version=$LATEST,invoked_function_arn=arn:aws:lambda:us-east-2:844534048980:function:test,client_context=None,identity=CognitoIdentity([cognito_identity_id=None,cognito_identity_pool_id=None])])"
    }
  }
}

# interaction
{
    "type": 2,
    "token": "A_UNIQUE_TOKEN",
    "member": {
        "user": {
            "id": "53908232506183680",
            "username": "Mason",
            "avatar": "a_d5efa99b3eeaa7dd43acca82f5692432",
            "discriminator": "1337",
            "public_flags": 131141
        },
        "roles": ["539082325061836999"],
        "premium_since": null,
        "permissions": "2147483647",
        "pending": false,
        "nick": null,
        "mute": false,
        "joined_at": "2017-03-13T19:19:14.040000+00:00",
        "is_pending": false,
        "deaf": false
    },
    "id": "786008729715212338",
    "guild_id": "290926798626357999",
    "app_permissions": "442368",
    "guild_locale": "en-US",
    "locale": "en-US",
    "data": {
        "options": [{
            "type": 3,
            "name": "cardname",
            "value": "The Gitrog Monster"
        }],
        "type": 1,
        "name": "cardsearch",
        "id": "771825006014889984"
    },
    "channel_id": "645027906669510667"
}