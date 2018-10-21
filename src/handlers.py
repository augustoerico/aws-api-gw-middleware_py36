import json


def auth_context_on_error(e: Exception) -> dict:
    return {
        "statusCode": 401,
        "body": json.dumps({
            "errors": [{"message": "Unauthorized.\n" + str(e)}]
        })
    }


def payload_parser_on_error(e: Exception) -> dict:
    return {
        "statusCode": 400,
        "body": json.dumps({
            "errors": [{"message": "Bad request.\n" + str(e)}]
        })
    }


def to_response_api_gw(r: dict) -> dict:
    if r and isinstance(r, dict):
        if r.get('statusCode') and isinstance(r['statusCode'], int):
            if r.get('body'):
                if isinstance(r['body'], dict):
                    try:
                        body_str = json.dumps(r['body'])
                    except Exception as e:
                        return {
                            "statusCode": 500,
                            "body": json.dumps({
                                "errors": [{
                                    "message": "Error while returning response. Return body as string instead.\n"
                                               + str(e)
                                }]
                            })
                        }
                    else:
                        return {
                            "statusCode": r['statusCode'],
                            "body": body_str
                        }
                elif isinstance(r['body'], str):
                    return {k: v for k, v in r.items() if k in ['statusCode', 'body']}
                else:
                    return {
                        "statusCode": r['statusCode'],
                        "body": str(r['body'])
                    }
            else:
                return {k: v for k, v in r.items() if k in ['statusCode', 'body']}

    message = 'Invalid lambda return. Return "statusCode" (int) and "body" (str or dict, optional)'
    return {
        "statusCode": 500,
        "body": json.dumps({"errors": [{"message": message}]})
    }
