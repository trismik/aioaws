# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**aioaws** is a lightweight, dependency-minimal asyncio SDK for AWS services. It intentionally avoids boto3, implementing AWS Signature Version 4 authentication from scratch. Uses httpx for HTTP, pydantic for validation, and cryptography for SNS signature verification.

Supported services: S3, SES, SNS (webhook verification), SQS.

## Commands

- **Install**: `make install` (sets up pip-tools, pre-commit, and all deps)
- **Run all checks**: `make all` (lint + mypy + test with coverage)
- **Lint**: `make lint` (ruff check + format check)
- **Format**: `make format` (ruff fix + format)
- **Type check**: `make mypy`
- **Test**: `make test` (coverage run -m pytest)
- **Single test**: `coverage run -m pytest tests/test_s3.py::test_name -x`
- **Test with coverage HTML**: `make testcov`
- **Update lock files**: `make update-lockfiles`

## Architecture

### Core signing (`core.py`)
`AWSv4Auth` implements AWS Signature V4 from scratch. `AwsClient` wraps httpx `AsyncClient` with auth, used by S3 and SES clients. `AWSV4AuthFlow` is an httpx `Auth` subclass used by SQS (which passes auth via httpx's native auth parameter instead of manually setting headers).

### Service pattern
Each service module (s3, ses, sqs) defines its own config dataclass and client class. S3 and SES clients create an `AwsClient` internally. SQS takes a different approach — it uses `AWSV4AuthFlow` with httpx's auth system directly.

### Config protocols (`_types.py`)
`BaseConfigProtocol` and `S3ConfigProtocol` are typing Protocols. Config objects just need matching attributes (`aws_access_key`, `aws_secret_key`, `aws_region`, and optionally `aws_s3_bucket`/`aws_host`).

### Testing infrastructure
Tests use a local aiohttp dummy server (`tests/dummy_server.py`) with `foxglove.testing.DummyServer`. `tests/conftest.py` defines `CustomAsyncClient` that rewrites URLs to route S3/SES/SNS requests to the local server. `aioaws/testing.py` provides helpers for parsing SES raw emails and generating mock SES responses.

Some tests (`test_s3.py`, `test_ses.py`) have "real AWS" tests gated behind `TEST_AWS_ACCESS_KEY`/`TEST_AWS_SECRET_KEY` env vars (skipped when absent).

## Style

- Single quotes for strings (configured in ruff)
- Line length: 120
- Type hints required everywhere (mypy strict mode)
- Python 3.10+ (uses `X | Y` union syntax, not `Optional`/`Union`)
- Tests use `pytest` with `asyncio_mode = "auto"` (no need for `@pytest.mark.asyncio`)