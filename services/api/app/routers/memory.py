import redis
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.crypto import encrypt_secret, mask_secret
from app.deps import get_db
from app.models import RedisConfig, User
from app.routers.auth import get_current_user

router = APIRouter(prefix="/memory", tags=["memory"])


@router.put("/redis")
def save_redis(url: str, namespace: str = "default", db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    existing = db.exec(select(RedisConfig).where(RedisConfig.tenant_id == user.tenant_id)).first()
    if not existing:
        existing = RedisConfig(tenant_id=user.tenant_id, url_encrypted="", namespace=namespace)
    existing.url_encrypted = encrypt_secret(url)
    existing.namespace = namespace
    existing.enabled = True
    db.add(existing)
    db.commit()
    db.refresh(existing)
    return {"id": existing.id, "url": mask_secret(url), "namespace": namespace}


@router.post("/redis/test")
def test_redis(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    config = db.exec(select(RedisConfig).where(RedisConfig.tenant_id == user.tenant_id)).first()
    if not config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Redis config not found")
    client = redis.from_url(config.get_url())
    try:
        client.ping()
    except redis.RedisError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return {"status": "ok", "namespace": config.namespace}
