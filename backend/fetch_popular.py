import httpx
url = 'https://openrouter.ai/api/v1/models'
response = httpx.get(url)
models = response.json().get('data', [])

free_models = []
for m in models:
    if m.get('pricing', {}).get('prompt') == '0' and m.get('pricing', {}).get('completion') == '0':
        free_models.append(m['id'])

print("Popular free models:")
for m in free_models:
    if 'google' in m or 'meta-llama' in m or 'mistral' in m:
        print(m)
