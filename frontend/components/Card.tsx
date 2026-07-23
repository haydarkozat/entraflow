import React from "react";

export function Card({
  title,
  subtitle,
  action,
  children,
  bodyPadding = true,
}: {
  title?: string;
  subtitle?: string;
  action?: React.ReactNode;
  children: React.ReactNode;
  bodyPadding?: boolean;
}) {
  return (
    <section className="card">
      {(title || action) && (
        <div className="card__head">
          <div>
            {title && <h2>{title}</h2>}
            {subtitle && <p>{subtitle}</p>}
          </div>
          {action}
        </div>
      )}
      <div className="card__body" style={bodyPadding ? undefined : { padding: 0 }}>
        {children}
      </div>
    </section>
  );
}
