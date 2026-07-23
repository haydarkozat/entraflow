// Handgezeichnete Inline-SVG-Icons (keine externe Icon-Bibliothek).
import React from "react";

type P = React.SVGProps<SVGSVGElement>;

const base = {
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 1.8,
  strokeLinecap: "round" as const,
  strokeLinejoin: "round" as const,
};

export const IconDashboard = (p: P) => (
  <svg {...base} {...p}>
    <rect x="3" y="3" width="7" height="9" rx="1.5" />
    <rect x="14" y="3" width="7" height="5" rx="1.5" />
    <rect x="14" y="12" width="7" height="9" rx="1.5" />
    <rect x="3" y="16" width="7" height="5" rx="1.5" />
  </svg>
);

export const IconLifecycle = (p: P) => (
  <svg {...base} {...p}>
    <path d="M21 12a9 9 0 1 1-3.5-7.1" />
    <path d="M21 4v4h-4" />
  </svg>
);

export const IconLicense = (p: P) => (
  <svg {...base} {...p}>
    <rect x="3" y="5" width="18" height="14" rx="2" />
    <path d="M3 10h18" />
    <path d="M7 15h4" />
  </svg>
);

export const IconShield = (p: P) => (
  <svg {...base} {...p}>
    <path d="M12 3l7 3v5c0 4.5-3 7.7-7 9-4-1.3-7-4.5-7-9V6l7-3z" />
    <path d="M9.2 12l1.9 1.9 3.8-3.8" />
  </svg>
);

export const IconAudit = (p: P) => (
  <svg {...base} {...p}>
    <path d="M8 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V5a2 2 0 0 0-2-2h-2" />
    <rect x="8" y="2" width="8" height="4" rx="1" />
    <path d="M8 11h8M8 15h5" />
  </svg>
);

export const IconUsers = (p: P) => (
  <svg {...base} {...p}>
    <circle cx="9" cy="8" r="3.2" />
    <path d="M3.5 20a5.5 5.5 0 0 1 11 0" />
    <path d="M16 5.2a3.2 3.2 0 0 1 0 6.1" />
    <path d="M17 20a5.5 5.5 0 0 0-3-4.9" />
  </svg>
);

export const IconUserCheck = (p: P) => (
  <svg {...base} {...p}>
    <circle cx="9" cy="8" r="3.4" />
    <path d="M3.5 20a5.5 5.5 0 0 1 11 0" />
    <path d="M16 12l2 2 3.5-3.5" />
  </svg>
);

export const IconGroup = (p: P) => (
  <svg {...base} {...p}>
    <rect x="3" y="3" width="7" height="7" rx="1.5" />
    <rect x="14" y="3" width="7" height="7" rx="1.5" />
    <rect x="3" y="14" width="7" height="7" rx="1.5" />
    <rect x="14" y="14" width="7" height="7" rx="1.5" />
  </svg>
);

export const IconRecords = (p: P) => (
  <svg {...base} {...p}>
    <ellipse cx="12" cy="5" rx="8" ry="3" />
    <path d="M4 5v6c0 1.7 3.6 3 8 3s8-1.3 8-3V5" />
    <path d="M4 11v6c0 1.7 3.6 3 8 3s8-1.3 8-3v-6" />
  </svg>
);

export const IconEuro = (p: P) => (
  <svg {...base} {...p}>
    <path d="M15 5.5A6.5 6.5 0 1 0 15 18.5" />
    <path d="M4 10h9M4 14h9" />
  </svg>
);

export const IconSeats = (p: P) => (
  <svg {...base} {...p}>
    <path d="M6 18v-6a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v6" />
    <path d="M4 18h16" />
    <path d="M8 10V7a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v3" />
  </svg>
);

export const IconReset = (p: P) => (
  <svg {...base} {...p}>
    <path d="M3 12a9 9 0 1 0 2.6-6.3" />
    <path d="M3 4v4h4" />
  </svg>
);

export const IconPlay = (p: P) => (
  <svg {...base} {...p}>
    <path d="M6 4.5v15l13-7.5z" />
  </svg>
);

export const IconRocket = (p: P) => (
  <svg {...base} {...p}>
    <path d="M5 15c-1.5 1.5-2 5-2 5s3.5-.5 5-2c.9-.9.9-2.3 0-3.2a2.2 2.2 0 0 0-3 .2z" />
    <path d="M9 12l3 3 4-1c3-1 5-4 5-9 0 0-8 0-9 5l-3 2z" />
    <circle cx="15" cy="9" r="1.4" />
  </svg>
);

export const IconPlus = (p: P) => (
  <svg {...base} {...p}>
    <path d="M12 5v14M5 12h14" />
  </svg>
);

export const IconInfo = (p: P) => (
  <svg {...base} {...p}>
    <circle cx="12" cy="12" r="9" />
    <path d="M12 11v5M12 8h.01" />
  </svg>
);

export const IconAlert = (p: P) => (
  <svg {...base} {...p}>
    <path d="M12 3l9 16H3z" />
    <path d="M12 9v5M12 17h.01" />
  </svg>
);

export const IconCheck = (p: P) => (
  <svg {...base} {...p}>
    <circle cx="12" cy="12" r="9" />
    <path d="M8.5 12l2.4 2.4 4.6-4.8" />
  </svg>
);

export const IconCloudOff = (p: P) => (
  <svg {...base} {...p}>
    <path d="M3 3l18 18" />
    <path d="M6.5 9A5 5 0 0 0 7 19h9" />
    <path d="M20 16.5A4 4 0 0 0 18 9h-1.3A6 6 0 0 0 9 5.2" />
  </svg>
);

export const IconChevron = (p: P) => (
  <svg {...base} {...p}>
    <path d="M9 6l6 6-6 6" />
  </svg>
);

export const IconLock = (p: P) => (
  <svg {...base} {...p}>
    <rect x="4.5" y="10.5" width="15" height="10" rx="2" />
    <path d="M8 10.5V7a4 4 0 0 1 8 0v3.5" />
  </svg>
);
