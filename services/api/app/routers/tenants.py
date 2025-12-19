from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.deps import get_db
from app.models import Tenant, User
from app.routers.auth import get_current_user

router = APIRouter(prefix="/tenants", tags=["tenants"])


@router.get("/current")
def get_current_tenant(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tenant = db.get(Tenant, user.tenant_id)
    return tenant


@router.post("/invite")
def invite_teammate(email: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    # simplistic invite that just creates a member
    member = User(email=email, password_hash="", tenant_id=user.tenant_id, role="member")
    db.add(member)
    db.commit()
    db.refresh(member)
    return {"invited_user_id": member.id, "tenant_id": user.tenant_id}
