from fastapi import APIRouter, HTTPException
from src.openclaw_skill.openclaw_event_adapter import adapt_openclaw_event

router = APIRouter()


@router.post("/api/skill/invoke")
def skill_invoke(event: dict) -> dict:
    """
    OpenClaw plugin entry point. Receives a normalized channel event from the
    openclaw-aivan plugin and routes it through the B-side/M-side procurement
    workflow. OpenClaw owns all channel I/O; Giraffe owns procurement logic.
    """
    try:
        return adapt_openclaw_event(event)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
