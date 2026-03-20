import urllib.request
import json
import traceback

url = "https://openrouter.ai/api/v1/chat/completions"
api_key = "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"
data = json.dumps({
    "model": "google/gemini-2.5-flash",
    "messages": [{"role": "user", "content": "Hello"}]
}).encode('utf-8')

headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}

req = urllib.request.Request(url, data=data, headers=headers)
try:
    with urllib.request.urlopen(req) as response:
        result = response.read().decode('utf-8')
        print("SUCCESS:", result)
except urllib.error.HTTPError as e:
    print(f"HTTP ERROR: {e.code}")
    print("RESPONSE BODY:", e.read().decode('utf-8'))
except Exception as e:
    print("OTHER ERROR:")
    traceback.print_exc()
