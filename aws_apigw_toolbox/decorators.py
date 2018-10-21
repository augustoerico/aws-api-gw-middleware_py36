import json
from typing import Callable, Any

from aws_apigw_toolbox import handlers as h


def middleware(
        auth_context_handler: Callable[[dict], None] = None,
        auth_context_on_error_handler: Callable[[Exception], dict] = h.auth_context_on_error,
        payload_parser: Callable[[dict], dict] = None,
        payload_parser_on_error_handler: Callable[[Exception], dict] = h.payload_parser_on_error
):
    def decorator(lambda_handler: Callable[[dict, Any], dict]):

        def lambda_handlers_wrapper(event: dict, context):

            # Lambda authorizer
            if auth_context_handler:
                if not isinstance(event, dict):
                    return h.to_response_api_gw(
                        auth_context_on_error_handler(
                            NotImplementedError('Middleware only supports event as dict')
                        )
                    )

                authorizer_context = (event.get('requestContext') or {}).get('authorizer')
                try:
                    auth_context_handler(authorizer_context)

                except Exception as e:
                    try:
                        response = h.to_response_api_gw(auth_context_on_error_handler(e))

                    except Exception as e:
                        response = {
                            "statusCode": 500,
                            "body": json.dumps({
                                "errors": [{
                                    "message": "Unhandled exception on auth_context_on_error_handler.\n" + str(e)
                                }]
                            })
                        }

                    return response

            # Parser
            if payload_parser:
                try:
                    payload = payload_parser(event.get('body'))
                    event = {**event, "middleware": {"body": payload}}

                except Exception as e:
                    try:
                        response = h.to_response_api_gw(payload_parser_on_error_handler(e))

                    except Exception as e:
                        response = {
                            "statusCode": 500,
                            "body": json.dumps({
                                "errors": [{
                                    "message": "Unhandled exception on payload_parser_on_error_handler.\n" + str(e)
                                }]
                            })
                        }

                    return response

            try:
                response = lambda_handler(event, context)
                return h.to_response_api_gw(response)

            except Exception as e:
                return {
                    "statusCode": 500,
                    "body": json.dumps({
                        "errors": [{"message": str(e)}]
                    })
                }

        return lambda_handlers_wrapper

    return decorator
