from fastapi import APIRouter, Depends, HTTPException

from ..services.conversation_service import ConversationService

router = APIRouter(prefix="/api", tags=["state"])


def get_service() -> ConversationService:
    from ..main import conversation_service
    return conversation_service


@router.get("/state/{thread_id}")
def state(thread_id: str, service: ConversationService = Depends(get_service)):
    try:
        return service.state(thread_id)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "category": "state_error",
                "message": str(exc),
            },
        ) from exc
