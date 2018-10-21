import json

from src.middleware import aws_api_gateway


def assert_common_conditions(response: dict) -> None:
    assert isinstance(response, dict)

    assert response.get('statusCode') and isinstance(response['statusCode'], int)

    if response.get('body'):
        assert isinstance(response['body'], str)

    assert not any(key not in ['statusCode', 'body'] for key in response)


def test_1():
    # given
    @aws_api_gateway()
    def any_lambda_handler(_, __):
        return {
            "statusCode": 200
        }

    # when
    response = any_lambda_handler(None, None)

    # then
    assert_common_conditions(response)


def test_2():
    # given
    response_body = {
        "attr1": "value1",
        "attr2": 123,
        "attr3": 12.34
    }

    # and
    @aws_api_gateway()
    def any_lambda_handler(_, __):
        return {
            "statusCode": 200,
            "body": response_body
        }

    # when
    response = any_lambda_handler(None, None)

    # then
    assert_common_conditions(response)

    # and
    assert json.loads(response['body']) == response_body


def test_3():
    # given
    response_body = {
        "attr1": "value1",
        "attr2": 123,
        "attr3": 12.34
    }

    # and
    @aws_api_gateway()
    def any_lambda_handler(_, __):
        return {
            "statusCode": 200,
            "body": json.dumps(response_body)
        }

    # when
    response = any_lambda_handler(None, None)

    # then
    assert_common_conditions(response)

    # and
    assert json.loads(response['body']) == response_body


def test_4():
    from decimal import Decimal
    # given
    response_body = {
        "attr1": "value1",
        "attr2": Decimal(123),
        "attr3": Decimal(12.34)
    }

    # and
    @aws_api_gateway()
    def any_lambda_handler(_, __):
        return {
            "statusCode": 200,
            "body": json.dumps(response_body)
        }

    # when
    response = any_lambda_handler(None, None)

    # then
    assert_common_conditions(response)

    # and
    rsp_body = json.loads(response['body'])
    assert rsp_body.get('errors') and isinstance(rsp_body['errors'], list)
    assert all(e.get('message') for e in rsp_body['errors'])


def test_5():
    # given
    e_message = 'Unhandled exception'

    # and
    @aws_api_gateway()
    def any_lambda_handler(_, __):
        raise Exception(e_message)

    # when
    response = any_lambda_handler(None, None)

    # then
    assert_common_conditions(response)
    assert response['statusCode'] == 500

    # and
    rsp_body = json.loads(response['body'])
    assert rsp_body.get('errors') and isinstance(rsp_body['errors'], list)
    assert any(
        e_message in e.get('message')
        for e in rsp_body['errors']
    )


# now with handlers ====================================================================================================

def test_6():
    # given
    def auth_handler(_):
        return

    def parser(data: dict):
        return {**data, "attr0": "value0"}

    # and
    @aws_api_gateway(
        auth_context_handler=auth_handler,
        payload_parser=parser
    )
    def any_lambda_handler(event_, __):
        return {
            "statusCode": 200,
            "body": event_['middleware']['body']
        }

    # and
    event = {
        "body": {"attr1": 1},
        "requestContext": {
            "authorizer": {
                "attr1": "value1"
            }
        }
    }

    # when
    response = any_lambda_handler(event, None)

    # then
    assert_common_conditions(response)

    # and
    rsp_body = json.loads(response['body'])
    assert rsp_body == {"attr1": 1, "attr0": "value0"}


def test_7():
    # given
    def auth_handler(_):
        raise Exception("Unhandled exception in auth")

    # and
    @aws_api_gateway(
        auth_context_handler=auth_handler
    )
    def any_lambda_handler(_, __):
        return {
            "statusCode": 200
        }

    # when
    response = any_lambda_handler(dict(), None)

    # then
    assert_common_conditions(response)
    assert response['statusCode'] == 401
    assert 'Unauthorized' in response['body']
