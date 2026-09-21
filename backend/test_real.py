import httpx
import uuid
import time

API_URL = 'http://127.0.0.1:8000/api'
thread_id = f"test-real-{uuid.uuid4()}"

MODEL_A = 'liquid/lfm-2.5-2.6b:free'
MODEL_B = 'nex-agi/nex-n2.5-mini:free'

print("--- REQUEST 1 ---")
r1 = httpx.post(f"{API_URL}/chat", json={
    "thread_id": thread_id,
    "message": "Explain what LangGraph is in two sentences.",
    "provider": "openrouter",
    "model": MODEL_A
}, timeout=60.0)

if r1.status_code == 200:
    data1 = r1.json()
    print("SUCCESS")
    print("Response:", data1.get("response"))
else:
    print("ERROR:", r1.status_code, r1.text)

print("\n--- REQUEST 2 ---")
r2 = httpx.post(f"{API_URL}/chat", json={
    "thread_id": thread_id,
    "message": "Now explain why persistent checkpoints are useful.",
    "provider": "openrouter",
    "model": MODEL_B
}, timeout=60.0)

if r2.status_code == 200:
    data2 = r2.json()
    print("SUCCESS")
    print("Response:", data2.get("response"))
else:
    print("ERROR:", r2.status_code, r2.text)

print("\n--- VERIFYING THREAD ---")
r3 = httpx.get(f"{API_URL}/threads/{thread_id}")
if r3.status_code == 200:
    t_data = r3.json()
    messages = t_data.get("messages", [])
    print("Messages count:", len(messages))
    if len(messages) >= 4:
        print("Thread successfully maintained across models!")
    else:
        print("WARNING: Thread did not accumulate messages correctly.")
else:
    print("ERROR fetching thread:", r3.status_code, r3.text)

