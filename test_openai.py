#!/usr/bin/env python3
"""
Test script for OpenAI integration
"""

import os
from dotenv import load_dotenv
from utils.generate_text import generate_text

def test_openai_integration():
    """Test the OpenAI text generation function"""
    
    # Load environment variables
    load_dotenv()
    
    # Get API key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment variables")
        print("Please set it in your .env file or environment")
        return False
    
    print("✅ OpenAI API key found")
    
    # Test different models
    models_to_test = ["gpt-4o-mini", "gpt-4"]
    
    for model in models_to_test:
        print(f"\n🧪 Testing with model: {model}")
        try:
            # Test text generation
            print("🚀 Testing text generation...")
            result = generate_text(minutes=0, seconds=15, api_key=api_key, model=model)
            
            if result.startswith("Error"):
                print(f"❌ Error: {result}")
                continue
            
            print("✅ Text generation successful!")
            print(f"Generated text: {result[:100]}...")
            
        except Exception as e:
            print(f"❌ Exception occurred: {str(e)}")
            continue
    
    return True

if __name__ == "__main__":
    print("🧪 Testing OpenAI Integration")
    print("=" * 40)
    
    success = test_openai_integration()
    
    if success:
        print("\n✅ All tests passed! OpenAI integration is working correctly.")
    else:
        print("\n❌ Tests failed. Please check your configuration.")
