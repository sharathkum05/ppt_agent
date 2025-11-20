"""Simple test script to verify Anthropic API key is working"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
import os
import anthropic
from anthropic import APIError

# Load environment variables
load_dotenv()

def test_anthropic_key():
    """Test if Anthropic API key is valid and working"""
    print("=" * 60)
    print("Testing Anthropic API Key")
    print("=" * 60)
    
    # Step 1: Check if API key exists
    print("\n1. Checking API key in .env file...")
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    
    if not api_key:
        print("   ✗ ANTHROPIC_API_KEY not found in .env file")
        print("   Please add your API key to .env file:")
        print("   ANTHROPIC_API_KEY=sk-ant-api03-...")
        return False
    
    if api_key.startswith("your_anthropic_api_key_here") or api_key.startswith("sk-ant-api03-") == False:
        if not api_key.startswith("sk-ant-api03-"):
            print("   ⚠ API key format looks incorrect")
            print(f"   Key starts with: {api_key[:20]}...")
        else:
            print(f"   ✓ API key found: {api_key[:20]}...")
    else:
        print(f"   ✓ API key found: {api_key[:20]}...")
    
    # Step 2: Initialize Anthropic client
    print("\n2. Initializing Anthropic client...")
    try:
        client = anthropic.Anthropic(api_key=api_key)
        print("   ✓ Client initialized successfully")
    except Exception as e:
        print(f"   ✗ Failed to initialize client: {str(e)}")
        return False
    
    # Step 3: Make a simple API call
    print("\n3. Making test API call...")
    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=100,
            messages=[
                {
                    "role": "user",
                    "content": "Say 'Hello, API is working!' and nothing else."
                }
            ]
        )
        
        # Extract response text
        if response.content and len(response.content) > 0:
            response_text = response.content[0].text
            print(f"   ✓ API call successful!")
            print(f"   Response: {response_text}")
            return True
        else:
            print("   ⚠ API call succeeded but no content returned")
            return True
            
    except APIError as e:
        print(f"   ✗ APIError occurred")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Error attributes: {dir(e)}")
        
        # Try to safely extract error information
        try:
            if hasattr(e, 'status_code'):
                print(f"   Status code: {e.status_code}")
            if hasattr(e, 'message'):
                print(f"   Message: {e.message}")
            if hasattr(e, 'body'):
                print(f"   Body type: {type(e.body)}")
                if isinstance(e.body, dict):
                    print(f"   Body: {e.body}")
        except Exception as attr_error:
            print(f"   Could not access error attributes: {attr_error}")
        
        # Try to get string representation safely
        try:
            error_str = str(e)
            print(f"   Error string: {error_str}")
        except Exception as str_error:
            print(f"   Could not convert to string: {str_error}")
            print(f"   This is the root cause of our problem!")
        
        return False
        
    except Exception as e:
        print(f"   ✗ Unexpected error: {type(e).__name__}")
        print(f"   Error: {str(e)}")
        return False


if __name__ == "__main__":
    print("\n")
    success = test_anthropic_key()
    print("\n" + "=" * 60)
    if success:
        print("✓ ANTHROPIC API KEY IS WORKING!")
        print("The issue is likely in how we handle errors in the main app.")
    else:
        print("✗ ANTHROPIC API KEY TEST FAILED")
        print("Please check your API key and try again.")
    print("=" * 60 + "\n")

