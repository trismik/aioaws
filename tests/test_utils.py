from datetime import datetime

import pytest
from httpx import URL, AsyncClient

from aioaws import _types, _utils, core


def test_get_config_attr():
    class Foo:
        a = 'alpha'
        b = 2

    f = Foo()

    assert _utils.get_config_attr(f, 'a') == 'alpha'
    with pytest.raises(TypeError, match='config has not attribute foobar'):
        _utils.get_config_attr(f, 'foobar')
    with pytest.raises(TypeError, match='config.b must be a string not int'):
        _utils.get_config_attr(f, 'b')


def test_types():
    assert hasattr(_types, 'BaseConfigProtocol')
    assert hasattr(_types, 'S3ConfigProtocol')


def test_auth_headers_with_session_token(mocker):
    mocker.patch('aioaws.core.utcnow', return_value=datetime(2032, 1, 1))
    auth = core.AWSv4Auth(
        aws_secret_key='test-secret',
        aws_access_key='test-access',
        region='us-east-1',
        service='bedrock',
        session_token='test-session-token',
    )
    headers = auth.auth_headers(
        'POST',
        URL('https://bedrock-runtime.us-east-1.amazonaws.com/model/test/invoke'),
        data=b'{"hello": "world"}',
        content_type='application/json',
    )
    assert headers['x-amz-security-token'] == 'test-session-token'
    # verify it's a signed header (appears in Authorization)
    assert 'x-amz-security-token' in headers['authorization']


def test_aws_client_session_token_invalid_type():
    class Config:
        aws_access_key = 'test-access'
        aws_secret_key = 'test-secret'
        aws_region = 'us-east-1'
        aws_host = 'email.us-east-1.amazonaws.com'
        aws_session_token = 123

    with pytest.raises(ValueError, match='aws_session_token must be a string, not int'):
        core.AwsClient(AsyncClient(), Config(), 'ses')


def test_auth_headers_without_session_token(mocker):
    mocker.patch('aioaws.core.utcnow', return_value=datetime(2032, 1, 1))
    auth = core.AWSv4Auth(
        aws_secret_key='test-secret',
        aws_access_key='test-access',
        region='us-east-1',
        service='bedrock',
    )
    headers = auth.auth_headers(
        'POST',
        URL('https://bedrock-runtime.us-east-1.amazonaws.com/model/test/invoke'),
        data=b'{}',
        content_type='application/json',
    )
    assert 'x-amz-security-token' not in headers


@pytest.mark.asyncio
async def test_response_error_xml(client: AsyncClient):
    response = await client.get(f'http://localhost:{client.port}/xml-error/')
    assert response.status_code == 456
    e = core.RequestError(response)
    assert str(e).endswith('(XML formatted by aioaws)')


@pytest.mark.asyncio
async def test_response_error_not_xml(client: AsyncClient):
    response = await client.get(f'http://localhost:{client.port}/status/400/')
    assert response.status_code == 400
    e = core.RequestError(response)
    assert str(e) == (
        f'unexpected response from GET "http://localhost:{client.port}/status/400/": 400, response:\n'
        'test response with status 400'
    )
