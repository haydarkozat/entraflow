"""Einlesen des Soll-Zustands aus einem Schulverwaltungs-Export (SchILD-NRW / ASV-BW).

Erwartetes CSV-Format (Semikolon-getrennt, wie die deutschen Exporte üblicherweise):

    quell_id;vorname;nachname;rolle;klasse;aktiv
    S-10231;Mia;Ostermann;student;8a;1

``rolle`` ∈ {student, teacher, staff}. ``klasse`` bleibt bei Lehrkräften/Verwaltung
leer. ``aktiv`` = 0 markiert eine:n Abgänger:in bereits im Quellsystem.
"""

from __future__ import annotations

import csv
import io
from pathlib import Path

from ..domain import DesiredUser, Role

_ROLE_ALIASES = {
    "student": Role.STUDENT, "sus": Role.STUDENT, "schueler": Role.STUDENT, "schüler": Role.STUDENT,
    "teacher": Role.TEACHER, "lehrkraft": Role.TEACHER, "lehrer": Role.TEACHER,
    "staff": Role.STAFF, "verwaltung": Role.STAFF, "sekretariat": Role.STAFF,
}


def parse_rows(reader: csv.DictReader) -> list[DesiredUser]:
    users: list[DesiredUser] = []
    for row in reader:
        row = {(k or "").strip().lower(): (v or "").strip() for k, v in row.items()}
        role_raw = row.get("rolle", "").lower()
        role = _ROLE_ALIASES.get(role_raw)
        if role is None:
            raise ValueError(f"Unbekannte Rolle '{role_raw}' für {row.get('quell_id')}")
        klasse = row.get("klasse") or None
        aktiv = row.get("aktiv", "1") not in {"0", "false", "nein", "inaktiv"}
        users.append(
            DesiredUser(
                given_name=row["vorname"],
                surname=row["nachname"],
                role=role,
                school_class=klasse,
                source_id=row["quell_id"],
                active=aktiv,
            )
        )
    return users


def load_desired_from_csv(path: Path) -> list[DesiredUser]:
    text = Path(path).read_text(encoding="utf-8-sig")
    return parse_rows(csv.DictReader(io.StringIO(text), delimiter=";"))


def load_desired_from_text(text: str) -> list[DesiredUser]:
    return parse_rows(csv.DictReader(io.StringIO(text), delimiter=";"))
