"""Produktiver Graph-Client gegen einen echten Microsoft-365-Tenant.

Implementiert dieselbe Schnittstelle wie ``InMemoryGraphClient``. Authentifiziert
per OAuth2-Client-Credentials-Flow (App-Registrierung in Entra ID) und spricht die
REST-Endpunkte von Microsoft Graph v1.0 an.

Benötigte Application-Permissions (admin-consent):
    User.ReadWrite.All, Group.ReadWrite.All, Organization.Read.All,
    Directory.Read.All, AuditLog.Read.All

Aktiviert über ``GRAPH_MODE=graph`` samt MS_TENANT_ID / MS_CLIENT_ID /
MS_CLIENT_SECRET. Bewusst schlank gehalten: Er demonstriert die 1:1-Abbildung
auf die Graph-REST-API, ohne den Demo-Betrieb an einen echten Tenant zu binden.
"""

from __future__ import annotations

import time

import httpx

from ..config import Settings
from .client import (
    GraphError,
    GraphGroup,
    GraphUser,
    SubscribedSku,
)


class HttpGraphClient:
    def __init__(self, settings: Settings) -> None:
        self._s = settings
        self._token: str | None = None
        self._token_exp: float = 0.0
        self._http = httpx.Client(base_url=settings.graph_base_url, timeout=30.0)

    # ---- Auth (Client-Credentials-Flow) -----------------------------------
    def _access_token(self) -> str:
        if self._token and time.time() < self._token_exp - 60:
            return self._token
        url = f"https://login.microsoftonline.com/{self._s.tenant_id}/oauth2/v2.0/token"
        resp = httpx.post(
            url,
            data={
                "client_id": self._s.client_id,
                "client_secret": self._s.client_secret,
                "scope": "https://graph.microsoft.com/.default",
                "grant_type": "client_credentials",
            },
            timeout=30.0,
        )
        if resp.status_code != 200:
            raise GraphError(f"Token-Anfrage fehlgeschlagen: {resp.status_code} {resp.text}")
        payload = resp.json()
        self._token = payload["access_token"]
        self._token_exp = time.time() + int(payload.get("expires_in", 3600))
        return self._token

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._access_token()}", "Content-Type": "application/json"}

    def _get(self, path: str, params: dict | None = None) -> dict:
        r = self._http.get(path, headers=self._headers(), params=params)
        if r.status_code >= 400:
            raise GraphError(f"GET {path} -> {r.status_code}: {r.text}")
        return r.json()

    def _paged(self, path: str, params: dict | None = None) -> list[dict]:
        items: list[dict] = []
        data = self._get(path, params)
        items.extend(data.get("value", []))
        while data.get("@odata.nextLink"):
            r = self._http.get(data["@odata.nextLink"], headers=self._headers())
            data = r.json()
            items.extend(data.get("value", []))
        return items

    # ---- Nutzer ------------------------------------------------------------
    def list_users(self) -> list[GraphUser]:
        fields = "id,userPrincipalName,displayName,givenName,surname,accountEnabled,usageLocation,assignedLicenses,employeeId,userType,signInActivity"
        raw = self._paged("/users", {"$select": fields, "$top": 999})
        return [GraphUser(**{k: v for k, v in u.items() if k in GraphUser.model_fields}) for u in raw]

    def get_user(self, user_id: str) -> GraphUser | None:
        try:
            return GraphUser(**self._get(f"/users/{user_id}"))
        except GraphError:
            return None

    def find_user_by_upn(self, upn: str) -> GraphUser | None:
        return self.get_user(upn)

    def create_user(self, user: GraphUser) -> GraphUser:
        body = {
            "accountEnabled": user.accountEnabled,
            "displayName": user.displayName,
            "givenName": user.givenName,
            "surname": user.surname,
            "userPrincipalName": user.userPrincipalName,
            "mailNickname": user.userPrincipalName.split("@")[0],
            "usageLocation": user.usageLocation,
            "employeeId": user.employeeId,
            "passwordProfile": {
                "forceChangePasswordNextSignIn": True,
                "password": _initial_password(),
            },
        }
        r = self._http.post("/users", headers=self._headers(), json=body)
        if r.status_code >= 400:
            raise GraphError(f"create_user -> {r.status_code}: {r.text}")
        return GraphUser(**r.json())

    def set_account_enabled(self, user_id: str, enabled: bool) -> None:
        self._patch_user(user_id, {"accountEnabled": enabled})

    def assign_license(self, user_id: str, sku_id: str) -> None:
        body = {"addLicenses": [{"skuId": sku_id, "disabledPlans": []}], "removeLicenses": []}
        self._post(f"/users/{user_id}/assignLicense", body)

    def remove_license(self, user_id: str, sku_id: str) -> None:
        body = {"addLicenses": [], "removeLicenses": [sku_id]}
        self._post(f"/users/{user_id}/assignLicense", body)

    def convert_to_shared_mailbox(self, user_id: str) -> None:
        # Exchange-Online-Operation (Set-Mailbox -Type Shared) – hier als Marker dokumentiert.
        self._patch_user(user_id, {"employeeType": "SharedMailbox"})

    def schedule_deletion(self, user_id: str, delete_after_iso: str) -> None:
        # In Produktion i. d. R. über einen Lifecycle-Workflow / Access-Review abgebildet.
        self._patch_user(user_id, {"employeeLeaveDateTime": delete_after_iso})

    # ---- Gruppen -----------------------------------------------------------
    def list_groups(self) -> list[GraphGroup]:
        raw = self._paged("/groups", {"$select": "id,displayName,mailNickname,groupTypes", "$top": 999})
        return [
            GraphGroup(id=g["id"], displayName=g["displayName"], mailNickname=g.get("mailNickname", ""))
            for g in raw
        ]

    def get_group_by_nickname(self, nickname: str) -> GraphGroup | None:
        raw = self._paged("/groups", {"$filter": f"mailNickname eq '{nickname}'"})
        if not raw:
            return None
        g = raw[0]
        return GraphGroup(id=g["id"], displayName=g["displayName"], mailNickname=g.get("mailNickname", ""))

    def ensure_group(self, display_name: str, nickname: str, group_type: str) -> GraphGroup:
        existing = self.get_group_by_nickname(nickname)
        if existing:
            return existing
        body = {
            "displayName": display_name,
            "mailNickname": nickname,
            "mailEnabled": group_type == "Unified",
            "securityEnabled": group_type == "Security",
            "groupTypes": ["Unified"] if group_type == "Unified" else [],
        }
        r = self._http.post("/groups", headers=self._headers(), json=body)
        if r.status_code >= 400:
            raise GraphError(f"ensure_group -> {r.status_code}: {r.text}")
        g = r.json()
        return GraphGroup(id=g["id"], displayName=g["displayName"], mailNickname=g.get("mailNickname", ""))

    def add_member(self, group_id: str, user_id: str) -> None:
        body = {"@odata.id": f"{self._s.graph_base_url}/directoryObjects/{user_id}"}
        self._post(f"/groups/{group_id}/members/$ref", body)

    def remove_member(self, group_id: str, user_id: str) -> None:
        r = self._http.delete(f"/groups/{group_id}/members/{user_id}/$ref", headers=self._headers())
        if r.status_code >= 400 and r.status_code != 404:
            raise GraphError(f"remove_member -> {r.status_code}: {r.text}")

    # ---- Lizenzen ----------------------------------------------------------
    def list_subscribed_skus(self) -> list[SubscribedSku]:
        raw = self._paged("/subscribedSkus")
        return [SubscribedSku(**{k: v for k, v in s.items() if k in SubscribedSku.model_fields}) for s in raw]

    # ---- Intern ------------------------------------------------------------
    def _post(self, path: str, body: dict) -> None:
        r = self._http.post(path, headers=self._headers(), json=body)
        if r.status_code >= 400:
            raise GraphError(f"POST {path} -> {r.status_code}: {r.text}")

    def _patch_user(self, user_id: str, body: dict) -> None:
        r = self._http.patch(f"/users/{user_id}", headers=self._headers(), json=body)
        if r.status_code >= 400:
            raise GraphError(f"PATCH /users/{user_id} -> {r.status_code}: {r.text}")


def _initial_password() -> str:
    import secrets

    return "Ef!" + secrets.token_urlsafe(16)
