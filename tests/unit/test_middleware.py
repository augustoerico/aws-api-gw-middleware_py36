import json

from src.middleware import aws_api_gateway


def assert_common_conditions(response: dict) -> None:
    assert isinstance(response, dict)

    assert response.get('statusCode') and isinstance(response['statusCode'], int)

    if response.get('body'):
        assert isinstance(response['body'], str)

    assert not any(key not in ['statusCode', 'body'] for key in response)


def test_should_1():
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


def test_should_2():
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
