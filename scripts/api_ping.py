
import os
import sys
import time
from openai import OpenAI

api_key = os.environ.get("DEEPSEEK_API_KEY")
if not api_key:
    print("❌ API Key not found")
    sys.exit(1)

client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

print("📡 Pinging DeepSeek API...")
start = time.time()

try:
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": "Ping. Reply with 'Pong' only."}],
        max_tokens=5,
        timeout=30
    )
    duration = time.time() - start
    print(f"✅ Success! Response: {response.choices[0].message.content}")
    print(f"⏱️ Duration: {duration:.2f}s")
except Exception as e:
    print(f"❌ Failed: {e}")
    sys.exit(1)
