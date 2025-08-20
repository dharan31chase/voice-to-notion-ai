import openai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Debug: Print what we're loading (remove API key for security)
print(f"Looking for .env file...")
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    print(f"✅ API key found: {api_key[:10]}...")
else:
    print("❌ No API key found in environment")
    exit()

# Initialize OpenAI client
client = openai.OpenAI(api_key=api_key)

def test_openai():
    try:
        print("Making API call to OpenAI...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say hello world!"}],
            max_tokens=50
        )
        print("✅ OpenAI connected successfully!")
        print(f"Response: {response.choices[0].message.content}")
        return True
    except Exception as e:
        print(f"❌ OpenAI error: {e}")
        return False

if __name__ == "__main__":
    test_openai()