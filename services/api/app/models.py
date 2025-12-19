from datetime import datetime
from typing import Optional

from sqlalchemy import Text
from sqlmodel import Column, Field, JSON, Relationship, SQLModel

from app.core.crypto import decrypt_secret, encrypt_secret


class Tenant(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    domain: Optional[str] = Field(default=None)
    plan: Optional[str] = Field(default="free")
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    users: list["User"] = Relationship(back_populates="tenant")
    evo_instances: list["EvolutionInstance"] = Relationship(back_populates="tenant")
    provider_configs: list["ProviderConfig"] = Relationship(back_populates="tenant")
    redis_configs: list["RedisConfig"] = Relationship(back_populates="tenant")
    chat_sessions: list["ChatSession"] = Relationship(back_populates="tenant")


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    password_hash: str
    tenant_id: int = Field(foreign_key="tenant.id")
    role: str = Field(default="owner")
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    tenant: Tenant = Relationship(back_populates="users")


class EvolutionInstance(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id")
    instance_key: str = Field(index=True, unique=True)
    status: str = Field(default="awaiting_qr")
    webhook_url: str
    qr_code_svg: Optional[str] = None
    last_sync: Optional[datetime] = None

    tenant: Tenant = Relationship(back_populates="evo_instances")


class ProviderConfig(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id")
    kind: str
    display_name: str
    secrets_encrypted: str = Field(sa_column=Column("secrets_encrypted", Text))
    meta: dict = Field(default_factory=dict, sa_column=Column(JSON))
    enabled: bool = Field(default=False)

    tenant: Tenant = Relationship(back_populates="provider_configs")

    def set_secret(self, secret: str) -> None:
        self.secrets_encrypted = encrypt_secret(secret)

    def get_secret(self) -> str:
        return decrypt_secret(self.secrets_encrypted)


class RedisConfig(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id")
    url_encrypted: str
    namespace: Optional[str] = None
    enabled: bool = Field(default=False)
    last_tested_at: Optional[datetime] = None
    status: str = Field(default="unknown")

    tenant: Tenant = Relationship(back_populates="redis_configs")

    def set_url(self, url: str) -> None:
        self.url_encrypted = encrypt_secret(url)

    def get_url(self) -> str:
        return decrypt_secret(self.url_encrypted)


class ChatSession(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id")
    whatsapp_number: str
    provider_id: Optional[int] = Field(default=None, foreign_key="providerconfig.id")
    redis_config_id: Optional[int] = Field(default=None, foreign_key="redisconfig.id")
    thread_key: Optional[str] = None

    tenant: Tenant = Relationship(back_populates="chat_sessions")
    messages: list["MessageLog"] = Relationship(back_populates="chat_session")


class MessageLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    chat_session_id: int = Field(foreign_key="chatsession.id")
    direction: str
    payload: dict = Field(default_factory=dict, sa_column=Column(JSON))
    tokens_used: Optional[int] = None
    latency_ms: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    chat_session: ChatSession = Relationship(back_populates="messages")


class AuditEvent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id")
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    action: str
    details: dict = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
