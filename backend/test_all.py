import requests
base = 'http://127.0.0.1:8000/api'
t1 = 't1_normal'
t2 = 't2_clarify'
t3 = 't3_hitl'
print('A. Normal:', requests.post(f'{base}/chat', json={'thread_id': t1, 'message': 'hello'}).json().get('trace', []))
print('B. Clarify:', requests.post(f'{base}/chat', json={'thread_id': t2, 'message': 'fix it'}).json().get('trace', []))
print('C. HITL:', requests.post(f'{base}/chat', json={'thread_id': t3, 'message': 'approve this'}).json().get('pending_interrupt', False))
print('D. Resume Appr:', requests.post(f'{base}/resume', json={'thread_id': t3, 'decision': 'approve'}).json().get('trace', []))
t4 = 't4_hitl'
requests.post(f'{base}/chat', json={'thread_id': t4, 'message': 'approve this'})
print('E. Resume Rej:', requests.post(f'{base}/resume', json={'thread_id': t4, 'decision': 'reject'}).json().get('trace', []))
print('F. Persist:', requests.get(f'{base}/state/{t1}').json().get('state', {}).get('intent', ''))
