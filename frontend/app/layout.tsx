import type { Metadata } from "next";
import "./globals.css";
import { Sidebar } from "@/components/Sidebar";
import { TopBar } from "@/components/TopBar";

export const metadata: Metadata = {
  title: "EntraFlow – Entra-ID Lifecycle für Schulen",
  description:
    "Automatisierung des Microsoft-365-/Entra-ID-Lebenszyklus, Lizenz-Governance und DSGVO-Compliance für Schulen.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="de">
      <body>
        <div className="app">
          <Sidebar />
          <div className="main">
            <TopBar />
            <main className="content">{children}</main>
          </div>
        </div>
      </body>
    </html>
  );
}
