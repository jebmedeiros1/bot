from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.core.crypto import encrypt_secret, mask_secret
from app.deps import get_db
from app.models import ProviderConfig, User
from app.routers.auth import get_current_user

router = APIRouter(prefix="/providers", tags=["providers"])


@router.put("/{provider_id}")
def upsert_provider(
    provider_id: int,
    kind: str,
    display_name: str,
    secret: str,
    meta: dict | None = None,
    enabled: bool = True,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    provider = db.get(ProviderConfig, provider_id)
    if provider and provider.tenant_id != user.tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Provider not found")
    if not provider:
        provider = ProviderConfig(id=provider_id, tenant_id=user.tenant_id, kind=kind, display_name=display_name, secrets_encrypted="")
    provider.display_name = display_name
    provider.kind = kind
    provider.secrets_encrypted = encrypt_secret(secret)
    provider.meta = meta or {}
    provider.enabled = enabled
    db.add(provider)
    db.commit()
    db.refresh(provider)
    return {"id": provider.id, "secret": mask_secret(secret), "enabled": provider.enabled}


@router.post("/{provider_id}/test")
def test_provider(provider_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    provider = db.get(ProviderConfig, provider_id)
    if not provider or provider.tenant_id != user.tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Provider not found")
    return {"status": "ok", "provider": provider.display_name, "kind": provider.kind}
