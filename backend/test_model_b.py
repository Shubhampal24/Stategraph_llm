from app.core.config import settings
from app.llm.openrouter import OpenRouterLLM

MODEL_B = 'nex-agi/nex-n2.5-mini:free'

print('\n--- MODEL B ---')
llm_b = OpenRouterLLM(api_key=settings.openrouter_api_key, model=MODEL_B)
messages_b = [{'role': 'user', 'content': 'Explain PostgreSQL checkpoint persistence in two sentences.'}]

try:
    response_b = llm_b.invoke(messages_b)
    print('SUCCESS')
    print('Response:', response_b)
except Exception as e:
    print('ERROR:', e)
