from datetime import datetime

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.deps import get_db
from app.models import ChatSession, MessageLog

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/evolution/global")
def evolution_webhook(payload: dict, db: Session = Depends(get_db)):
    instance_key = payload.get("instanceKey")
    message = payload.get("message") or {}
    whatsapp_number = message.get("from") or "unknown"

    chat = db.exec(select(ChatSession).where(ChatSession.thread_key == instance_key, ChatSession.whatsapp_number == whatsapp_number)).first()
    if not chat:
        chat = ChatSession(tenant_id=payload.get("tenant_id", 0), whatsapp_number=whatsapp_number, thread_key=instance_key)
        db.add(chat)
        db.flush()
    log = MessageLog(chat_session_id=chat.id, direction="inbound", payload=payload, created_at=datetime.utcnow())
    db.add(log)
    db.commit()
    return {"status": "received", "chat_session_id": chat.id}
