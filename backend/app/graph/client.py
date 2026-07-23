"""Die Graph-Schnittstelle, gegen die die gesamte Lebenszyklus-Logik programmiert ist.

Die Datenformen (``GraphUser``, ``GraphGroup``, ``SubscribedSku``) folgen exakt den
JSON-Schemata von Microsoft Graph v1.0. Dadurch ist der In-Memory-Mock
(``memory.py``) verhaltensgleich zum echten Client (``http_client.py``) – der
Wechsel auf einen produktiven Tenant ist reine Konfiguration, kein Code-Umbau.
"""

from __future__ import annotations

from typing import Protocol

from pydantic import BaseModel, Field


class AssignedLicense(BaseModel):
    skuId: str
    disabledPlans: list[str] = Field(default_factory=list)


class SignInActivity(BaseModel):
    lastSignInDateTime: str | None = None  # ISO-8601, wie von Graph geliefert


class GraphUser(BaseModel):
    id: str
    userPrincipalName: str
    displayName: str
    givenName: str | None = None
    surname: str | None = None
    accountEnabled: bool = True
    usageLocation: str | None = None
    assignedLicenses: list[AssignedLicense] = Field(default_factory=list)
    # Herkunftsschlüssel aus dem Quellsystem – in Graph über employeeId abgebildet
    employeeId: str | None = None
    # "Member" (Konto), "Guest", oder intern "Service"/"SharedMailbox"
    userType: str = "Member"
    mailboxType: str = "UserMailbox"
    createdDateTime: str | None = None  # ISO-8601, wie von Graph geliefert
    signInActivity: SignInActivity | None = None
    deletionScheduledFor: str | None = None  # ISO-Datum; nur EntraFlow-intern


class GraphGroup(BaseModel):
    id: str
    displayName: str
    mailNickname: str
    members: list[str] = Field(default_factory=list)  # Liste von user-ids
    groupType: str = "Unified"  # "Unified" (M365/Team), "Security"


class PrepaidUnits(BaseModel):
    enabled: int = 0
    suspended: int = 0
    warning: int = 0


class SubscribedSku(BaseModel):
    skuId: str
    skuPartNumber: str
    prepaidUnits: PrepaidUnits
    consumedUnits: int = 0


class GraphError(RuntimeError):
    """Analog zu einer Graph-4xx/5xx-Antwort."""


class GraphClient(Protocol):
    """Die Menge an Operationen, die die Lebenszyklus-Engine benötigt."""

    def list_users(self) -> list[GraphUser]: ...

    def get_user(self, user_id: str) -> GraphUser | None: ...

    def find_user_by_upn(self, upn: str) -> GraphUser | None: ...

    def create_user(self, user: GraphUser) -> GraphUser: ...

    def set_account_enabled(self, user_id: str, enabled: bool) -> None: ...

    def assign_license(self, user_id: str, sku_id: str) -> None: ...

    def remove_license(self, user_id: str, sku_id: str) -> None: ...

    def list_groups(self) -> list[GraphGroup]: ...

    def get_group_by_nickname(self, nickname: str) -> GraphGroup | None: ...

    def ensure_group(self, display_name: str, nickname: str, group_type: str) -> GraphGroup: ...

    def add_member(self, group_id: str, user_id: str) -> None: ...

    def remove_member(self, group_id: str, user_id: str) -> None: ...

    def convert_to_shared_mailbox(self, user_id: str) -> None: ...

    def schedule_deletion(self, user_id: str, delete_after_iso: str) -> None: ...

    def list_subscribed_skus(self) -> list[SubscribedSku]: ...
