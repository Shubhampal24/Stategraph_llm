import httpx

url = 'https://openrouter.ai/api/v1/models'
response = httpx.get(url)
models = response.json().get('data', [])

free_models = []
for m in models:
    if m.get('pricing', {}).get('prompt') == '0' and m.get('pricing', {}).get('completion') == '0':
        free_models.append(m['id'])

print("Found", len(free_models), "free models")
print("First 10 free models:")
for m in free_models[:10]:
    print(m)
