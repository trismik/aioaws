"""
Bedrock usage demo.

Usage:
    AWS_ACCESS_KEY=... AWS_SECRET_KEY=... [AWS_SESSION_TOKEN=...] python examples/bedrock_demo.py
"""
import asyncio
import os

from httpx import AsyncClient

from aioaws.bedrock import BedrockClient, BedrockConfig


async def main():
    config = BedrockConfig(
        aws_access_key=os.environ['AWS_ACCESS_KEY_ID'],
        aws_secret_key=os.environ['AWS_SECRET_ACCESS_KEY'],
        aws_region=os.environ.get('AWS_REGION', 'us-east-1'),
        aws_session_token=os.environ.get('AWS_SESSION_TOKEN'),
    )

    async with AsyncClient(timeout=60) as client:
        bedrock = BedrockClient(client, config)

        # --- Converse API (unified format, works with any Bedrock model) ---
        print('=== Converse API ===')
        response = await bedrock.converse(
            model='global.anthropic.claude-haiku-4-5-20251001-v1:0',
            body={
                'messages': [
                    {'role': 'user', 'content': [{'text': 'Explain quantum computing in one sentence.'}]},
                ],
                'inferenceConfig': {'maxTokens': 256, 'temperature': 0.7},
            },
        )
        text = response['output']['message']['content'][0]['text']
        usage = response['usage']
        print(f'Response: {text}')
        print(f'Tokens: {usage["inputTokens"]} in, {usage["outputTokens"]} out')

        # --- InvokeModel API (Anthropic-native format) ---
        print('\n=== InvokeModel API ===')
        response = await bedrock.invoke(
            model='global.anthropic.claude-haiku-4-5-20251001-v1:0',
            body={
                'anthropic_version': 'bedrock-2023-05-31',
                'max_tokens': 256,
                'messages': [{'role': 'user', 'content': 'What is 2+2?'}],
            },
        )
        print(f'Response: {response["content"][0]["text"]}')


asyncio.run(main())
