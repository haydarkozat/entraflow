"""Lizenz-Governance & Kosten-Optimierung.

Findet ungenutzte und fehlgeleitete Lizenzen und beziffert die monatliche
Einsparung in EUR. In Schulen mit tausenden Konten summieren sich „vergessene"
Seats schnell – hier werden sie sichtbar und rückgewinnbar.
"""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field

from ..config import Settings
from ..graph.client import GraphClient
from ..policies import LICENSE_CATALOG, price_for_sku_id


class SkuUsage(BaseModel):
    sku_part_number: str
    label: str
    capacity: int
    consumed: int
    available: int
    monthly_price_eur: float
    monthly_cost_eur: float


class Recommendation(BaseModel):
    kind: str            # inactive | disabled_licensed | duplicate_license
    upn: str
    display_name: str
    sku_part_number: str
    detail: str
    monthly_saving_eur: float


class OptimizationReport(BaseModel):
    reference_date: date
    usage: list[SkuUsage]
    recommendations: list[Recommendation] = Field(default_factory=list)
    total_monthly_saving_eur: float = 0.0
    reclaimable_seats: int = 0


class LicenseOptimizer:
    def __init__(self, client: GraphClient, settings: Settings) -> None:
        self._client = client
        self._s = settings

    def analyze(self) -> OptimizationReport:
        ref = self._s.reference_date
        threshold = self._s.inactivity_threshold_days

        usage = [
            SkuUsage(
                sku_part_number=sku.skuPartNumber,
                label=_label(sku.skuPartNumber),
                capacity=sku.prepaidUnits.enabled,
                consumed=sku.consumedUnits,
                available=sku.prepaidUnits.enabled - sku.consumedUnits,
                monthly_price_eur=price_for_sku_id(sku.skuId),
                monthly_cost_eur=round(sku.consumedUnits * price_for_sku_id(sku.skuId), 2),
            )
            for sku in self._client.list_subscribed_skus()
        ]

        recs: list[Recommendation] = []
        for user in self._client.list_users():
            catalog_licenses = [l for l in user.assignedLicenses if _is_catalog(l.skuId)]
            if not catalog_licenses:
                continue

            # 1) Deaktivierte Konten, die noch Lizenzen binden -> geleakte Seats.
            if not user.accountEnabled:
                for lic in catalog_licenses:
                    recs.append(_rec("disabled_licensed", user, lic.skuId,
                                     "Konto deaktiviert, Lizenz noch gebunden."))
                continue

            # 2) Mehrfachlizenzierung aus dem Katalog -> konsolidieren.
            if len(catalog_licenses) > 1:
                for lic in catalog_licenses[1:]:
                    recs.append(_rec("duplicate_license", user, lic.skuId,
                                     "Mehrfachlizenzierung – zweite Katalog-Lizenz überflüssig."))

            # 3) Aktive, aber lange inaktive Konten mit kostenpflichtiger Lizenz.
            #    Frisch angelegte Konten (jünger als die Schwelle) werden NICHT als
            #    inaktiv gewertet – sonst würde jeder Joiner fälschlich markiert.
            inactive_days = _inactivity_days(user, ref, threshold)
            if inactive_days is not None:
                for lic in catalog_licenses:
                    if price_for_sku_id(lic.skuId) > 0:
                        recs.append(_rec("inactive", user, lic.skuId,
                                         f"Kostenpflichtige Lizenz, {inactive_days}"))

        total = round(sum(r.monthly_saving_eur for r in recs), 2)
        return OptimizationReport(
            reference_date=ref,
            usage=usage,
            recommendations=recs,
            total_monthly_saving_eur=total,
            reclaimable_seats=len(recs),
        )


def _rec(kind: str, user, sku_id: str, detail: str) -> Recommendation:
    return Recommendation(
        kind=kind,
        upn=user.userPrincipalName,
        display_name=user.displayName,
        sku_part_number=_label(_part_number(sku_id)),
        detail=detail,
        monthly_saving_eur=round(price_for_sku_id(sku_id), 2),
    )


def _is_catalog(sku_id: str) -> bool:
    return any(p.sku_id == sku_id for p in LICENSE_CATALOG.values())


def _part_number(sku_id: str) -> str:
    for p in LICENSE_CATALOG.values():
        if p.sku_id == sku_id:
            return p.sku_part_number
    return sku_id


def _label(part_number: str) -> str:
    for p in LICENSE_CATALOG.values():
        if p.sku_part_number == part_number:
            return p.label
    return part_number


def _inactivity_days(user, ref: date, threshold: int) -> str | None:
    """Liefert eine Begründung, wenn das Konto als inaktiv gilt, sonst None.

    - Letzte Anmeldung älter als die Schwelle  -> "seit N Tagen inaktiv".
    - Nie angemeldet, aber Konto älter als Schwelle -> "seit Anlage nie genutzt".
    - Nie angemeldet und Konto jung (frischer Joiner) -> nicht inaktiv.
    """
    last = _parse_date(user.signInActivity.lastSignInDateTime if user.signInActivity else None)
    if last is not None:
        days = (ref - last).days
        return f"seit {days} Tagen inaktiv (Schwelle {threshold})" if days >= threshold else None

    created = _parse_date(user.createdDateTime)
    if created is not None and (ref - created).days >= threshold:
        return f"seit Anlage ({created.isoformat()}) nie genutzt"
    return None


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value[:10])
    except ValueError:
        return None
