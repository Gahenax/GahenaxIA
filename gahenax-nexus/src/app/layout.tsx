import type { Metadata } from "next";
import { Inter, Plus_Jakarta_Sans, Space_Mono } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], weight: ["300", "400", "500", "600", "700"], variable: '--font-inter', display: 'swap' });
const jakarta = Plus_Jakarta_Sans({ subsets: ["latin"], weight: ["300", "400", "500", "600", "700", "800"], variable: '--font-jakarta', display: 'swap' });
const mono = Space_Mono({ subsets: ["latin"], weight: ["400", "700"], variable: '--font-mono', display: 'swap' });

export const metadata: Metadata = {
  title: "Gahenax AI Solutions — Infraestructura de Crecimiento & OEDA Analytics",
  description:
    "Construimos arquitectura digital, automatizamos operaciones y aceleramos negocios con infraestructura tecnológica real. Desarrollo Web, Node.js y Estrategia OEDA.",
  keywords: "infraestructura digital, automatización empresarial, arquitectura web, consultoría OEDA, n8n, CRM, Gahenax",
  manifest: "/manifest.json",
  openGraph: {
    title: "Gahenax AI Solutions",
    description: "Infraestructura de crecimiento para la nueva economía.",
    url: "https://gahenaxaisolutions.com",
    siteName: "Gahenax AI Solutions",
    locale: "es_ES",
    type: "website",
    images: [{
      url: "https://gahenaxaisolutions.com/og-image.jpg",
      width: 1200,
      height: 630,
      alt: "Gahenax AI Solutions",
    }],
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
    <html lang="es" className={`${inter.variable} ${jakarta.variable} ${mono.variable}`}>
      <body>{children}</body>
    </html>
  );
}
