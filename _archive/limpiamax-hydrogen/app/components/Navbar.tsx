import {useEffect, useState} from 'react';
import {Link} from 'react-router';

export function Navbar() {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 60);
    window.addEventListener('scroll', onScroll, {passive: true});
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  return (
    <>
      <nav className={`navbar${scrolled ? ' scrolled' : ''}`} role="navigation" aria-label="Navegación principal">
        <div className="container">
          <div className="navbar-brand">
            <div>
              <div className="navbar-logo">
                Limpia<span>max</span>
              </div>
              <div className="navbar-tagline">Servicios Profesionales</div>
            </div>
          </div>

          <ul className="navbar-nav">
            <li><a href="#servicios">Servicios</a></li>
            <li><a href="#nosotros">Nosotros</a></li>
            <li><a href="#proceso">Proceso</a></li>
            <li><a href="#testimonios">Testimonios</a></li>
          </ul>

          <a
            href="https://wa.me/18091234567?text=Hola%2C%20quiero%20solicitar%20una%20cotización"
            className="btn btn-primary navbar-cta"
            target="_blank"
            rel="noopener noreferrer"
            id="nav-whatsapp-cta"
          >
             Cotizar Ahora
          </a>

          <button className="hamburger" aria-label="Abrir menú" aria-expanded="false">
            <span />
            <span />
            <span />
          </button>
        </div>
      </nav>

      {/* Floating WhatsApp */}
      <a
        href="https://wa.me/18091234567?text=Hola%2C%20quiero%20solicitar%20una%20cotización"
        className="whatsapp-float"
        target="_blank"
        rel="noopener noreferrer"
        aria-label="Contáctanos por WhatsApp"
        id="whatsapp-float-btn"
      >
        <span className="whatsapp-float-ring" />
        
      </a>
    </>
  );
}
