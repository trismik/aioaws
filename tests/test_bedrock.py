import pytest
from httpx import AsyncClient

from aioaws.bedrock import BedrockClient, BedrockConfig
from aioaws.core import RequestError


def test_bedrock_config():
    config = BedrockConfig(
        aws_access_key='AKIA...',
        aws_secret_key='secret',
        aws_region='us-east-1',
    )
    assert config.aws_session_token is None


def test_bedrock_config_with_session_token():
    config = BedrockConfig(
        aws_access_key='AKIA...',
        aws_secret_key='secret',
        aws_region='us-east-1',
        aws_session_token='token123',
    )
    assert config.aws_session_token == 'token123'


async def test_bedrock_client_base_url():
    config = BedrockConfig('key', 'secret', 'eu-west-1')
    async with AsyncClient() as http_client:
        bedrock = BedrockClient(http_client, config)
        assert bedrock._base_url == 'https://bedrock-runtime.eu-west-1.amazonaws.com'


async def test_invoke(client: AsyncClient):
    config = BedrockConfig('test_access_key', 'test_secret_key', 'us-east-1')
    bedrock = BedrockClient(client, config)
    response = await bedrock.invoke(
        model='global.anthropic.claude-haiku-4-5-20251001-v1:0',
        body={
            'anthropic_version': 'bedrock-2023-05-31',
            'max_tokens': 256,
            'messages': [{'role': 'user', 'content': 'Hello'}],
        },
    )
    assert response['content'][0]['text'] == 'mock invoke response'
    assert response['model'] == 'anthropic.claude-haiku-4-5-20251001-v1:0'


async def test_converse(client: AsyncClient):
    config = BedrockConfig('test_access_key', 'test_secret_key', 'us-east-1')
    bedrock = BedrockClient(client, config)
    response = await bedrock.converse(
        model='global.anthropic.claude-haiku-4-5-20251001-v1:0',
        body={
            'messages': [{'role': 'user', 'content': [{'text': 'Hello'}]}],
            'inferenceConfig': {'maxTokens': 256},
        },
    )
    assert response['output']['message']['content'][0]['text'] == 'mock converse response'
    assert response['stopReason'] == 'end_turn'
    assert response['usage']['inputTokens'] == 10


async def test_model_id_with_colon(client: AsyncClient):
    config = BedrockConfig('test_access_key', 'test_secret_key', 'us-east-1')
    bedrock = BedrockClient(client, config)
    response = await bedrock.converse(
        model='global.anthropic.claude-haiku-4-5-20251001-v1:0',
        body={'messages': [{'role': 'user', 'content': [{'text': 'test'}]}]},
    )
    assert response['output']['message']['content'][0]['text'] == 'mock converse response'


async def test_invoke_error(client: AsyncClient):
    config = BedrockConfig('test_access_key', 'test_secret_key', 'us-east-1')
    bedrock = BedrockClient(client, config)
    with pytest.raises(RequestError):
        await bedrock.invoke(model='nonexistent/model', body={})


async def test_real_converse(real_aws):
    config = BedrockConfig(
        aws_access_key=real_aws.access_key,
        aws_secret_key=real_aws.secret_key,
        aws_region='us-east-1',
        aws_session_token=real_aws.session_token,
    )
    async with AsyncClient(timeout=30) as http_client:
        bedrock = BedrockClient(http_client, config)
        response = await bedrock.converse(
            model='global.anthropic.claude-haiku-4-5-20251001-v1:0',
            body={
                'messages': [{'role': 'user', 'content': [{'text': 'Say just "hello"'}]}],
                'inferenceConfig': {'maxTokens': 32},
            },
        )
        assert 'output' in response
        text = response['output']['message']['content'][0]['text']
        assert len(text) > 0
        assert response['usage']['inputTokens'] > 0


async def test_real_invoke(real_aws):
    config = BedrockConfig(
        aws_access_key=real_aws.access_key,
        aws_secret_key=real_aws.secret_key,
        aws_region='us-east-1',
        aws_session_token=real_aws.session_token,
    )
    async with AsyncClient(timeout=30) as http_client:
        bedrock = BedrockClient(http_client, config)
        response = await bedrock.invoke(
            model='global.anthropic.claude-haiku-4-5-20251001-v1:0',
            body={
                'anthropic_version': 'bedrock-2023-05-31',
                'max_tokens': 32,
                'messages': [{'role': 'user', 'content': 'Say just "hello"'}],
            },
        )
        assert 'content' in response
        assert len(response['content'][0]['text']) > 0
