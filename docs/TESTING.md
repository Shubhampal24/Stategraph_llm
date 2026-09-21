# Testing

## Philosophy

The tests validate the assignment's difficult behavior, not only whether the server starts.

## Test categories

### Graph

- graph compiles
- normal route
- clarification route

### Persistence

- state is stored
- a new graph/service instance can read an existing thread checkpoint

### Human-in-the-loop

- interrupt occurs
- approval resumes
- rejection resumes

### API

- health
- validation
- chat
- approval/resume
- state inspection

## Free/offline tests

The test suite forces:

```env
LLM_PROVIDER=mock
```

Therefore it does not require:

- OpenAI
- Ollama
- internet
- paid API credits

## Run

```powershell
cd backend
python -m pytest -q
```

## Acceptance target

All tests should pass before the project is considered complete.
