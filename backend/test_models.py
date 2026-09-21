from app.core.config import settings
from app.llm.openrouter import OpenRouterLLM

MODEL_A = 'liquid/lfm-2.5-2.6b:free'
MODEL_B = 'thinkingmachines/inkling-small:free'

print('--- MODEL A ---')
llm_a = OpenRouterLLM(api_key=settings.openrouter_api_key, model=MODEL_A)
messages_a = [{'role': 'user', 'content': 'Explain what a LangGraph StateGraph is in two sentences.'}]

try:
    response_a = llm_a.invoke(messages_a)
    print('SUCCESS')
    print('Response:', response_a)
except Exception as e:
    print('ERROR:', e)

print('\n--- MODEL B ---')
llm_b = OpenRouterLLM(api_key=settings.openrouter_api_key, model=MODEL_B)
messages_b = [{'role': 'user', 'content': 'Explain PostgreSQL checkpoint persistence in two sentences.'}]

try:
    response_b = llm_b.invoke(messages_b)
    print('SUCCESS')
    print('Response:', response_b)
except Exception as e:
    print('ERROR:', e)
