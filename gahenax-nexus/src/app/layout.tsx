import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Gahenax AI Solutions — Infraestructura de Crecimiento & OEDA Analytics",
  description:
    "Construimos arquitectura digital, automatizamos operaciones y aceleramos negocios con infraestructura tecnológica real. Desarrollo Web, Node.js y Estrategia OEDA.",
  keywords: "infraestructura digital, automatización empresarial, arquitectura web, consultoría OEDA, n8n, CRM, Gahenax",
  openGraph: {
    title: "Gahenax AI Solutions",
    description: "Infraestructura de crecimiento para la nueva economía.",
    url: "https://gahenaxaisolutions.com",
    siteName: "Gahenax AI Solutions",
    locale: "es_ES",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Gahenax AI Solutions",
    description: "Arquitectura operacional y Sistemas de Captación Automatizada.",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es">
      <body>{children}</body>
    </html>
  );
}
