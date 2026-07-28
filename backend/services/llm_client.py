"""llm_client.py"""

import os
import logging

import boto3
from botocore.config import Config
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


def generate_text(prompt: str, max_tokens: int = 100) -> str | None:
    """
    Calls Bedrock to generate text from the given prompt. Returns None
    on any failure (timeout, throttling, malformed response, etc.) so
    the caller can fall back to a simpler rule-based justification."""
    try:
        client = boto3.client(
            "bedrock-runtime",
            region_name=os.getenv("AWS_REGION"),
            config=Config(connect_timeout=10, read_timeout=10, retries={"max_attempts": 1}),
        )
        response = client.converse(
            modelId=os.getenv("BEDROCK_MODEL_ID"),
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inferenceConfig={"maxTokens": max_tokens},
        )
        return response["output"]["message"]["content"][0]["text"].strip()
    except Exception as e:
        logger.warning("Bedrock call failed, falling back: %s", e)
        return None
