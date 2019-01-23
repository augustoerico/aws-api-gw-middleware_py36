import simplejson as json

headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Credentials": True
}


def auth_context_on_error(e: Exception) -> dict:
    return {
        "statusCode": 401,
        "body": json.dumps({
            "errors": [{"message": "Unauthorized.\n" + str(e)}]
        }),
        "headers": headers
    }


def payload_parser_on_error(e: Exception) -> dict:
    return {
        "statusCode": 400,
        "body": json.dumps({
            "errors": [{"message": "Bad request.\n" + str(e)}]
        }),
        "headers": headers
    }


def to_response_api_gw(r: dict) -> dict:

    if r and isinstance(r, dict):

        headers_ = {
            **headers,
            **(r.get('headers') or {})
        }

        if r.get('statusCode') and isinstance(r['statusCode'], int):

            if r.get('body'):
                if isinstance(r['body'], dict):
                    try:
                        response = {
                            "statusCode": r['statusCode'],
                            "body": json.dumps(r['body'])
                        }
                    except Exception as e:
                        response = {
                            "statusCode": 500,
                            "body": json.dumps({
                                "errors": [{
                                    "message": "Error while returning response. Return body as string instead.\n"
                                               + str(e)
                                }]
                            })
                        }

                else:
                    response = {
                        "statusCode": r['statusCode'],
                        "body": str(r['body'])
                    }
            else:
                response = {
                    "statusCode": r['statusCode']
                }

            response = {
                **response,
                "headers": headers_
            }

        else:
            message = 'Invalid lambda return. Should return "statusCode" (int) and "body" (str or dict, optional)'
            response = {
                "statusCode": 500,
                "body": json.dumps({"errors": [{"message": message}]}),
                "headers": headers_
            }

    else:
        message = f'Invalid lambda return. Should return `dict`, instead of {type(r)}'
        response = {
            "statusCode": 500,
            "body": json.dumps({"errors": [{"message": message}]}),
            "headers": headers
        }

    return response
