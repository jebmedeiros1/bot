from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.deps import get_db
from app.models import ChatSession, MessageLog, User
from app.routers.auth import get_current_user

router = APIRouter(prefix="/messages", tags=["messages"])


@router.post("/{chat_session_id}/send")
def send_message(chat_session_id: int, content: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    chat = db.get(ChatSession, chat_session_id)
    if not chat or chat.tenant_id != user.tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
    log = MessageLog(chat_session_id=chat.id, direction="outbound", payload={"content": content}, created_at=datetime.utcnow())
    db.add(log)
    db.commit()
    return {"status": "sent", "message_id": log.id}
