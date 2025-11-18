#!/usr/bin/env python
"""Test Azure OpenAI connection"""
from openai import AzureOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

print("Testing Azure OpenAI Connection...")
print("=" * 50)

api_key = os.getenv("AZURE_OPENAI_API_KEY", "")
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")

print(f"API Key (first 20 chars): {api_key[:20]}...")
print(f"Endpoint: {endpoint}")
print(f"Deployment: {deployment}")
print("=" * 50)

try:
    client = AzureOpenAI(
        api_key=api_key,
        api_version="2023-05-15",
        azure_endpoint=endpoint
    )
    
    print("Testing API call...")
    response = client.chat.completions.create(
        model=deployment,
        messages=[{"role": "user", "content": "Say OK if working"}],
        max_tokens=10
    )
    
    print("✅ Azure OpenAI Connection SUCCESSFUL!")
    print(f"Response: {response.choices[0].message.content}")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    print(f"Error Type: {type(e).__name__}")
