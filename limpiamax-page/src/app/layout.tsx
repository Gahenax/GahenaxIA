import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'LimpiaMAX - Limpiezas de casas y sofás en Barcelona',
  description:
    'Servicio profesional de limpieza de casas, sofás y alfombras en Barcelona. Desde €9.99. Reserva hoy.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <body>{children}</body>
    </html>
  );
}
