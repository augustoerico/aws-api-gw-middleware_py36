from setuptools import setup

config = {
    "name": "aws_apigw_toolbox",
    "version": "0.1.1",
    "packages": ["aws_apigw_toolbox"],
    "url": "https://github.com/augustoerico/aws-api-gw-middleware_py36",
    "description": "AWS API Gateway middleware for custom authorization and payload parser.",
    "classifiers": [],
    "install_requires": [
          "simplejson"
      ],
    "license": "MIT"
}

setup(**config)
