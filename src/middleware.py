import json
from typing import Callable, Any

from src import defaults as d


def aws_api_gateway(
        auth_context_handler: Callable[[dict], None] = None,
        auth_context_on_error_handler: Callable[[Exception], dict] = d.auth_context_on_error_handler,
        payload_parser: Callable[[dict], dict] = None,
        payload_parser_on_error_handler: Callable[[Exception], dict] = d.payload_parser_on_error_handler
):
    def middleware(lambda_handler: Callable[[dict, Any], dict]):

        def wrapper(event: dict, _):

            # Lambda authorizer
            if auth_context_handler:
                authorizer_context = (event.get('requestContext') or {}).get('authorizer')
                try:
                    auth_context_handler(authorizer_context)
                except Exception as e:
                    return auth_context_on_error_handler(e)

            # Parser
            if payload_parser:
                try:
                    payload = payload_parser(event.get('body'))
                except Exception as e:
                    return payload_parser_on_error_handler(e)

            try:
                return lambda_handler(event, _)
            except Exception as e:
                return {
                    "statusCode": 500,
                    "body": json.dumps({
                        "errors": [{"message": str(e)}]
                    })
                }

        return wrapper

    return middleware
