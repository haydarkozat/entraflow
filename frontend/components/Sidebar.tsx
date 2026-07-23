"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  IconDashboard,
  IconLifecycle,
  IconLicense,
  IconShield,
  IconAudit,
} from "./icons";

const NAV = [
  { href: "/", label: "Übersicht", Icon: IconDashboard },
  { href: "/lifecycle", label: "Lebenszyklus (JML)", Icon: IconLifecycle },
  { href: "/licenses", label: "Lizenz-Governance", Icon: IconLicense },
  { href: "/compliance", label: "DSGVO-Compliance", Icon: IconShield },
  { href: "/audit", label: "Audit-Log", Icon: IconAudit },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="sidebar">
      <div className="sidebar__brand">
        <svg
          className="sidebar__logo"
          viewBox="0 0 40 40"
          role="img"
          aria-label="EntraFlow Logo"
        >
          <defs>
            <linearGradient id="ef-grad" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0" stopColor="#5866d8" />
              <stop offset="1" stopColor="#3a49b8" />
            </linearGradient>
          </defs>
          <rect x="0" y="0" width="40" height="40" rx="11" fill="url(#ef-grad)" />
          <path
            d="M13 11h15v4H17v4h9v4h-9v4h11v4H13z"
            fill="#fff"
            fillOpacity="0.96"
          />
        </svg>
        <div className="sidebar__wordmark">
          <strong>EntraFlow</strong>
          <span>Entra-ID Lifecycle</span>
        </div>
      </div>

      <nav className="sidebar__nav">
        <div className="sidebar__section">Verwaltung</div>
        {NAV.map(({ href, label, Icon }) => {
          const active =
            href === "/" ? pathname === "/" : pathname.startsWith(href);
          return (
            <Link
              key={href}
              href={href}
              className={`navlink${active ? " active" : ""}`}
            >
              <Icon className="navlink__icon" />
              {label}
            </Link>
          );
        })}
      </nav>

      <div className="sidebar__foot">
        Microsoft 365 · Entra ID
        <br />
        Automatisierung für Schulen
      </div>
    </aside>
  );
}
