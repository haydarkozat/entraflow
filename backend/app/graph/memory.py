"""In-Memory-Implementierung von Microsoft Graph – verhaltensgleich zum Tenant.

Hält Nutzer, Gruppen und Lizenz-Kontingente konsistent: Beim Zuweisen/Entziehen
einer Lizenz werden ``consumedUnits`` mitgeführt, genau wie es der echte Graph
über ``subscribedSkus`` zurückmeldet. So testet die Lebenszyklus-Engine gegen
dieselbe Semantik, die sie später produktiv vorfindet.
"""

from __future__ import annotations

import json
import uuid
from pathlib import Path

from .client import (
    AssignedLicense,
    GraphError,
    GraphGroup,
    GraphUser,
    PrepaidUnits,
    SignInActivity,
    SubscribedSku,
)


class InMemoryGraphClient:
    def __init__(self) -> None:
        self._users: dict[str, GraphUser] = {}
        self._groups: dict[str, GraphGroup] = {}
        self._skus: dict[str, SubscribedSku] = {}

    # ---- Seed / Persistenz -------------------------------------------------
    @classmethod
    def from_seed(cls, path: Path) -> "InMemoryGraphClient":
        client = cls()
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        for sku in data.get("subscribedSkus", []):
            client._skus[sku["skuId"]] = SubscribedSku(**sku)
        for group in data.get("groups", []):
            client._groups[group["id"]] = GraphGroup(**group)
        for user in data.get("users", []):
            client._users[user["id"]] = GraphUser(**user)
        client._recompute_consumed()
        return client

    def snapshot(self) -> dict:
        return {
            "subscribedSkus": [s.model_dump() for s in self._skus.values()],
            "groups": [g.model_dump() for g in self._groups.values()],
            "users": [u.model_dump() for u in self._users.values()],
        }

    # ---- Nutzer ------------------------------------------------------------
    def list_users(self) -> list[GraphUser]:
        return list(self._users.values())

    def get_user(self, user_id: str) -> GraphUser | None:
        return self._users.get(user_id)

    def find_user_by_upn(self, upn: str) -> GraphUser | None:
        upn = upn.lower()
        for u in self._users.values():
            if u.userPrincipalName.lower() == upn:
                return u
        return None

    def create_user(self, user: GraphUser) -> GraphUser:
        if self.find_user_by_upn(user.userPrincipalName):
            raise GraphError(f"userPrincipalName bereits vergeben: {user.userPrincipalName}")
        if not user.id:
            user = user.model_copy(update={"id": str(uuid.uuid4())})
        self._users[user.id] = user
        self._recompute_consumed()
        return user

    def set_account_enabled(self, user_id: str, enabled: bool) -> None:
        self._require_user(user_id).accountEnabled = enabled

    def assign_license(self, user_id: str, sku_id: str) -> None:
        user = self._require_user(user_id)
        if sku_id not in self._skus:
            raise GraphError(f"Unbekannte skuId: {sku_id}")
        if any(l.skuId == sku_id for l in user.assignedLicenses):
            return  # idempotent
        sku = self._skus[sku_id]
        if sku.consumedUnits >= sku.prepaidUnits.enabled:
            raise GraphError(f"Kein freier Seat für {sku.skuPartNumber}")
        user.assignedLicenses.append(AssignedLicense(skuId=sku_id))
        self._recompute_consumed()

    def remove_license(self, user_id: str, sku_id: str) -> None:
        user = self._require_user(user_id)
        user.assignedLicenses = [l for l in user.assignedLicenses if l.skuId != sku_id]
        self._recompute_consumed()

    def convert_to_shared_mailbox(self, user_id: str) -> None:
        user = self._require_user(user_id)
        user.mailboxType = "SharedMailbox"
        user.userType = "SharedMailbox"

    def schedule_deletion(self, user_id: str, delete_after_iso: str) -> None:
        self._require_user(user_id).deletionScheduledFor = delete_after_iso

    # ---- Gruppen -----------------------------------------------------------
    def list_groups(self) -> list[GraphGroup]:
        return list(self._groups.values())

    def get_group_by_nickname(self, nickname: str) -> GraphGroup | None:
        for g in self._groups.values():
            if g.mailNickname.lower() == nickname.lower():
                return g
        return None

    def ensure_group(self, display_name: str, nickname: str, group_type: str) -> GraphGroup:
        existing = self.get_group_by_nickname(nickname)
        if existing:
            return existing
        group = GraphGroup(
            id=str(uuid.uuid4()),
            displayName=display_name,
            mailNickname=nickname,
            groupType=group_type,
        )
        self._groups[group.id] = group
        return group

    def add_member(self, group_id: str, user_id: str) -> None:
        group = self._require_group(group_id)
        if user_id not in group.members:
            group.members.append(user_id)

    def remove_member(self, group_id: str, user_id: str) -> None:
        group = self._require_group(group_id)
        if user_id in group.members:
            group.members.remove(user_id)

    # ---- Lizenzen ----------------------------------------------------------
    def list_subscribed_skus(self) -> list[SubscribedSku]:
        return list(self._skus.values())

    # ---- Intern ------------------------------------------------------------
    def _require_user(self, user_id: str) -> GraphUser:
        user = self._users.get(user_id)
        if not user:
            raise GraphError(f"Unbekannte Nutzer-id: {user_id}")
        return user

    def _require_group(self, group_id: str) -> GraphGroup:
        group = self._groups.get(group_id)
        if not group:
            raise GraphError(f"Unbekannte Gruppen-id: {group_id}")
        return group

    def _recompute_consumed(self) -> None:
        """Hält consumedUnits konsistent – so wie Graph es serverseitig tut."""
        counts: dict[str, int] = {sku_id: 0 for sku_id in self._skus}
        for user in self._users.values():
            for lic in user.assignedLicenses:
                if lic.skuId in counts:
                    counts[lic.skuId] += 1
        for sku_id, consumed in counts.items():
            self._skus[sku_id].consumedUnits = consumed
