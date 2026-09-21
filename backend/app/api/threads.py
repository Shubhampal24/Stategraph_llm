from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from ..db.repository import ThreadRepository

router = APIRouter(prefix="/api/threads", tags=["threads"])

@router.get("")
async def list_threads() -> List[Dict[str, Any]]:
    return await ThreadRepository.list_threads()

@router.get("/{thread_id}")
async def get_thread(thread_id: str) -> Dict[str, Any]:
    thread = await ThreadRepository.get_thread(thread_id)
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
        
    messages = await ThreadRepository.get_messages(thread_id)
    thread["messages"] = messages
    
    # If we want we could also fetch current state, but the frontend currently uses /api/state for that.
    # The requirement says "return: thread metadata, messages, current state if useful, pending HITL status if applicable"
    # We can get state using conversation_service.
    from ..main import conversation_service
    try:
        state = conversation_service.state(thread_id)
        thread["state"] = state
    except Exception:
        # LangGraph state might not exist yet if graph hasn't executed
        pass
        
    return thread
