from fastapi import APIRouter, Depends, HTTPException
from fastapi.concurrency import run_in_threadpool

from ..core.config import settings
from ..schemas.conversation import ChatRequest, ChatResponse, ResumeRequest
from ..services.conversation_service import ConversationService
from ..db.repository import ThreadRepository

router = APIRouter(prefix="/api", tags=["conversation"])

SUPPORTED_PROVIDERS = {
    "mock": ["mock-model"],
    "ollama": ["llama3.2:3b", "llama3:8b", "mistral"],
    "openrouter": ["liquid/lfm-2.5-2.6b:free", "nex-agi/nex-n2.5-mini:free"],
    "gemini": ["gemini-1.5-flash", "gemini-1.5-pro"]
}

def validate_provider_model(provider: str | None, model: str | None):
    p = (provider or settings.llm_provider).lower()
    
    if p not in SUPPORTED_PROVIDERS:
        raise HTTPException(status_code=400, detail=f"Invalid provider: {p}")
        
    if model:
        if model not in SUPPORTED_PROVIDERS[p]:
            raise HTTPException(status_code=400, detail=f"Invalid model '{model}' for provider '{p}'")


def get_service() -> ConversationService:
    from ..main import conversation_service
    return conversation_service


@router.get("/models")
def get_models():
    providers = []
    for pid, models in SUPPORTED_PROVIDERS.items():
        providers.append({"id": pid, "models": models})
    return {"providers": providers}


@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest, service: ConversationService = Depends(get_service)):
    message = payload.message.strip()
    if not message:
        raise HTTPException(status_code=422, detail="Message cannot be empty.")

    if len(message) > settings.max_message_length:
        raise HTTPException(status_code=413, detail="Message is too long.")

    validate_provider_model(payload.provider, payload.model)

    try:
        # Create thread if it doesn't exist. The title will be based on the first message.
        await ThreadRepository.create_thread(payload.thread_id.strip(), message)
        
        # Store user message
        await ThreadRepository.add_message(payload.thread_id.strip(), "user", message)
        
        # Execute graph synchronously in threadpool
        result = await run_in_threadpool(
            service.chat, 
            payload.thread_id.strip(), 
            message, 
            payload.provider, 
            payload.model
        )
        
        # Store assistant response if present
        if result.get("response"):
            await ThreadRepository.add_message(payload.thread_id.strip(), "assistant", result["response"])
            
        return result
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "category": "graph_execution_error",
                "message": str(exc),
            },
        ) from exc


@router.post("/resume", response_model=ChatResponse)
async def resume(
    payload: ResumeRequest,
    service: ConversationService = Depends(get_service),
):
    decision = payload.decision.strip().lower()
    if decision not in {"approve", "reject"}:
        raise HTTPException(
            status_code=422,
            detail="Decision must be approve or reject.",
        )

    validate_provider_model(payload.provider, payload.model)

    try:
        # Execute graph synchronously in threadpool
        result = await run_in_threadpool(
            service.resume,
            payload.thread_id.strip(),
            decision,
            payload.provider,
            payload.model
        )
        
        # Store assistant response if present
        if result.get("response"):
            await ThreadRepository.add_message(payload.thread_id.strip(), "assistant", result["response"])
            
        return result
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "category": "resume_error",
                "message": str(exc),
            },
        ) from exc
