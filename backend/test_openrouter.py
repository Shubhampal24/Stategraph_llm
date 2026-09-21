from app.core.config import settings
from app.llm.openrouter import OpenRouterLLM

print('KEY LOADED:', bool(settings.openrouter_api_key))

llm = OpenRouterLLM(api_key=settings.openrouter_api_key, model='openrouter/free')
messages = [{'role': 'user', 'content': 'Explain in one sentence what LangGraph is.'}]

try:
    response = llm.invoke(messages)
    print('RESPONSE:')
    print(response)
except Exception as e:
    print('ERROR:')
    print(e)
