from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.config import settings
from app.deps import get_db
from app.models import EvolutionInstance, User
from app.routers.auth import get_current_user

router = APIRouter(prefix="/evo", tags=["evolution"])


@router.post("/instances")
def create_instance(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    existing = db.exec(select(EvolutionInstance).where(EvolutionInstance.tenant_id == user.tenant_id)).first()
    if existing:
        return existing

    instance_key = f"tenant-{user.tenant_id}-primary"
    instance = EvolutionInstance(
        tenant_id=user.tenant_id,
        instance_key=instance_key,
        webhook_url=settings.webhook_global_url,
        status="awaiting_qr",
    )
    db.add(instance)
    db.commit()
    db.refresh(instance)
    return instance


@router.get("/instances/{instance_id}/status")
def instance_status(instance_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    instance = db.get(EvolutionInstance, instance_id)
    if not instance or instance.tenant_id != user.tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instance not found")
    return {"status": instance.status, "webhook_url": instance.webhook_url}


@router.get("/instances/{instance_id}/qr")
def instance_qr(instance_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    instance = db.get(EvolutionInstance, instance_id)
    if not instance or instance.tenant_id != user.tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instance not found")
    # placeholder qr for demo
    svg = "<svg viewBox='0 0 100 100'><rect width='100' height='100' fill='#7C3AED'/></svg>"
    instance.qr_code_svg = svg
    db.add(instance)
    db.commit()
    return {"qr_svg": svg, "status": instance.status}
