#!/usr/bin/env python3
"""Test Azure OpenAI connection"""
import os
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

api_key = os.getenv("AZURE_OPENAI_API_KEY")
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")

print("=" * 60)
print("AZURE OPENAI CONNECTION TEST")
print("=" * 60)
print(f"API Key: {api_key[:20]}..." if api_key else "API Key: NOT SET")
print(f"Endpoint: {endpoint}")
print(f"Deployment: {deployment}")
print("=" * 60)

try:
    client = AzureOpenAI(
        api_key=api_key,
        api_version="2023-05-15",
        azure_endpoint=endpoint
    )
    
    print("\n✓ Client created successfully")
    print("\nTesting chat completion...")
    
    response = client.chat.completions.create(
        model=deployment,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'Hello from Azure OpenAI!'"}
        ],
        max_tokens=50,
        temperature=0.7
    )
    
    print(f"✓ Response: {response.choices[0].message.content}")
    print("\n✅ Azure OpenAI connection is working!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print(f"\nError Type: {type(e).__name__}")
    print(f"Error Details: {str(e)}")
