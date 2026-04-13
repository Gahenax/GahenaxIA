import type {Route} from './+types/_index';
import {Navbar} from '~/components/Navbar';

export const meta: Route.MetaFunction = () => {
  return [
    {title: 'Limpiamax — Limpieza Profesional de Confianza'},
    {
      name: 'description',
      content:
        'Limpiamax ofrece servicios profesionales de limpieza residencial, comercial y post-obra. Calidad garantizada, personal certificado y precios accesibles.',
    },
    {name: 'keywords', content: 'limpieza profesional, limpieza residencial, limpieza comercial, limpieza post-obra'},
  ];
};

// No Shopify queries needed for the static landing page.
// When the store is connected, add Storefront API queries here.
export async function loader({context}: Route.LoaderArgs) {
  return {
    isShopLinked: Boolean(context.env.PUBLIC_STORE_DOMAIN),
  };
}

/*  DATA  */

const SERVICES = [
  {
    emoji: '',
    name: 'Limpieza Residencial',
    description:
      'Tu hogar reluciente de arriba a abajo. Incluye todas las habitaciones, baños, cocina y áreas comunes con productos premium.',
    price: 'Desde RD$1,500',
  },
  {
    emoji: '',
    name: 'Limpieza Comercial',
    description:
      'Oficinas, locales y establecimientos comerciales. Servicio diario, semanal o mensual según tus necesidades.',
    price: 'Desde RD$2,500',
  },
  {
    emoji: '',
    name: 'Limpieza Post-Obra',
    description:
      'Eliminamos polvo, residuos de construcción y dejamos tu espacio listo para habitar o inaugurar.',
    price: 'Desde RD$3,500',
  },
  {
    emoji: '',
    name: 'Limpieza Profunda',
    description:
      'Desinfección total con vapor y productos especializados. Ideal para mudanzas y limpieza semestral.',
    price: 'Desde RD$2,800',
  },
  {
    emoji: '',
    name: 'Limpieza de Vidrios',
    description:
      'Cristales, ventanas y fachadas con brillo garantizado. Trabajo en altura con equipo certificado.',
    price: 'Desde RD$800',
  },
  {
    emoji: '',
    name: 'Desinfección & Fumigación',
    description:
      'Eliminamos bacterias, virus y plagas con productos certificados y seguros para tu familia.',
    price: 'Desde RD$1,200',
  },
];

const TRUST_POINTS = [
  {
    emoji: '',
    title: 'Garantía Total',
    desc: 'Si no quedas 100% satisfecho, regresamos sin costo adicional. Tu satisfacción es nuestra prioridad.',
  },
  {
    emoji: '',
    title: 'Personal Certificado',
    desc: 'Todo nuestro equipo pasa por verificación de antecedentes y capacitación profesional continua.',
  },
  {
    emoji: '',
    title: 'Productos Ecológicos',
    desc: 'Usamos productos biodegradables que no dañan el medio ambiente ni la salud de tu familia.',
  },
  {
    emoji: '⏱',
    title: 'Puntuales Siempre',
    desc: 'Respetamos tu tiempo. Llegamos en el horario acordado o te compensamos por la espera.',
  },
  {
    emoji: '',
    title: 'Atención 24/7',
    desc: 'Disponibles por WhatsApp en cualquier momento. Cotización en menos de 10 minutos.',
  },
  {
    emoji: '',
    title: '+8 Años de Experiencia',
    desc: 'Más de 8 años en el mercado y más de 2,000 clientes satisfechos respaldan nuestra calidad.',
  },
];

const PROCESS_STEPS = [
  {emoji: '', title: 'Contáctanos', desc: 'Escríbenos por WhatsApp o llámanos para coordinar tu servicio.'},
  {emoji: '', title: 'Cotización', desc: 'Recibe tu presupuesto personalizado en menos de 10 minutos.'},
  {emoji: '', title: 'Agendamos', desc: 'Escogemos fecha y hora según tu disponibilidad. 100% flexible.'},
  {emoji: '', title: 'Resultados', desc: 'Nuestro equipo llega y deja todo impecable. ¡Garantizado!'},
];

const TESTIMONIALS = [
  {
    stars: 5,
    text: 'Increíble servicio. Llamé a Limpiamax para una limpieza post-obra y dejaron el apartamento como si fuera nuevo. Muy profesionales y puntuales.',
    initials: 'MA',
    name: 'María A.',
    role: 'Propietaria, Santo Domingo',
  },
  {
    stars: 5,
    text: 'Contratamos el servicio comercial para nuestra oficina y el nivel de detalle es impresionante. Ahora son nuestros proveedores permanentes.',
    initials: 'CR',
    name: 'Carlos R.',
    role: 'Gerente, Empresa de Tecnología',
  },
  {
    stars: 5,
    text: 'Excelente relación calidad-precio. Personal muy amable y el resultado final superó mis expectativas. Los recomiendo 100%.',
    initials: 'JP',
    name: 'Jennifer P.',
    role: 'Ama de casa, Santiago',
  },
];

/*  COMPONENT  */

export default function Homepage() {
  return (
    <>
      <Navbar />

      {/*  HERO  */}
      <section className="hero" id="inicio" aria-label="Inicio">
        <div className="hero-bg" role="presentation" />
        <div className="hero-gradient" role="presentation" />
        <div className="container">
          <div className="hero-content">
            <div className="hero-badge animate-fade-up">
              <span className="hero-badge-dot" />
              Servicio Profesional & Garantizado
            </div>

            <h1 className="hero-title animate-fade-up delay-1">
              Tu espacio,
              <span className="highlight">impecable.</span>
            </h1>

            <p className="hero-subtitle animate-fade-up delay-2">
              Limpieza profesional para hogares y empresas. Personal certificado,
              productos ecológicos y resultados que hablan por sí solos.
            </p>

            <div className="hero-actions animate-fade-up delay-3">
              <a
                href="https://wa.me/18091234567?text=Hola%2C%20quiero%20solicitar%20una%20cotización"
                className="btn btn-primary btn-lg"
                target="_blank"
                rel="noopener noreferrer"
                id="hero-whatsapp-cta"
              >
                 Solicitar Cotización
              </a>
              <a href="#servicios" className="btn btn-outline btn-lg" id="hero-see-services">
                Ver Servicios
              </a>
            </div>

            <div className="hero-stats animate-fade-up delay-4">
              <div className="hero-stat">
                <div className="hero-stat-num">2,000+</div>
                <div className="hero-stat-label">Clientes satisfechos</div>
              </div>
              <div className="hero-stat">
                <div className="hero-stat-num">8+</div>
                <div className="hero-stat-label">Años de experiencia</div>
              </div>
              <div className="hero-stat">
                <div className="hero-stat-num">100%</div>
                <div className="hero-stat-label">Garantía de calidad</div>
              </div>
            </div>
          </div>
        </div>

        <div className="hero-scroll" aria-hidden="true">
          <span>Scroll</span>
          <div className="scroll-arrow" />
        </div>
      </section>

      {/*  SERVICES  */}
      <section className="section services" id="servicios" aria-labelledby="servicios-title">
        <div className="container">
          <header className="section-header">
            <span className="section-label">Nuestros Servicios</span>
            <h2 className="h2 section-title" id="servicios-title">
              Todo lo que necesitas, <br />
              en un solo lugar
            </h2>
            <p className="section-sub">
              Desde limpieza residencial hasta desinfécciones especializadas. Adaptamos
              cada servicio a tus necesidades específicas.
            </p>
          </header>

          <div className="services-grid">
            {SERVICES.map((service) => (
              <article className="service-card" key={service.name}>
                <div className="service-icon" aria-hidden="true">{service.emoji}</div>
                <h3 className="service-name">{service.name}</h3>
                <p className="service-description">{service.description}</p>
                <span className="service-price"> {service.price}</span>
              </article>
            ))}
          </div>
        </div>
      </section>

      {/*  TRUST / WHY LIMPIAMAX  */}
      <section className="section trust" id="nosotros" aria-labelledby="trust-title">
        <div className="container">
          <header className="section-header">
            <span className="section-label">¿Por qué Limpiamax?</span>
            <h2 className="h2 section-title" id="trust-title">
              Comprometidos con la excelencia
            </h2>
            <p className="section-sub">
              No somos solo una empresa de limpieza. Somos tu socio de confianza para
              mantener tus espacios en perfectas condiciones.
            </p>
          </header>

          <div className="trust-grid">
            {TRUST_POINTS.map((point) => (
              <div className="trust-card" key={point.title}>
                <span className="trust-icon" aria-hidden="true">{point.emoji}</span>
                <h3 className="trust-title">{point.title}</h3>
                <p className="trust-desc">{point.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/*  PROCESS  */}
      <section className="section process" id="proceso" aria-labelledby="proceso-title">
        <div className="container">
          <header className="section-header">
            <span className="section-label">Cómo Funciona</span>
            <h2 className="h2 section-title" id="proceso-title">
              Simple, rápido y sin complicaciones
            </h2>
            <p className="section-sub">
              En 4 pasos sencillos tu espacio estará impecable.
            </p>
          </header>

          <div className="process-steps">
            {PROCESS_STEPS.map((step, i) => (
              <div className="process-step" key={step.title}>
                <div className="step-number" aria-hidden="true">
                  <span className="step-emoji">{step.emoji}</span>
                </div>
                <h3 className="step-title">{step.title}</h3>
                <p className="step-desc">{step.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/*  TESTIMONIALS  */}
      <section className="section testimonials" id="testimonios" aria-labelledby="testimonios-title">
        <div className="container">
          <header className="section-header">
            <span className="section-label">Testimonios</span>
            <h2 className="h2 section-title" id="testimonios-title">
              Lo que dicen nuestros clientes
            </h2>
            <p className="section-sub">
              Más de 2,000 familias y empresas confían en Limpiamax.
            </p>
          </header>

          <div className="testimonials-grid">
            {TESTIMONIALS.map((t) => (
              <blockquote className="testimonial-card" key={t.name}>
                <div className="testimonial-stars" aria-label={`${t.stars} estrellas`}>
                  {''.repeat(t.stars)}
                </div>
                <p className="testimonial-text">{t.text}</p>
                <footer className="testimonial-author">
                  <div className="author-avatar" aria-hidden="true">{t.initials}</div>
                  <div>
                    <div className="author-name">{t.name}</div>
                    <div className="author-role">{t.role}</div>
                  </div>
                </footer>
              </blockquote>
            ))}
          </div>
        </div>
      </section>

      {/*  CTA FINAL  */}
      <section className="section cta-section" aria-labelledby="cta-title">
        <div className="container">
          <h2 className="cta-title" id="cta-title">
            ¿Listo para un espacio impecable?
          </h2>
          <p className="cta-sub">
            Solicita tu cotización ahora mismo. Respuesta en menos de 10 minutos
            por WhatsApp.
          </p>
          <div className="cta-actions">
            <a
              href="https://wa.me/18091234567?text=Hola%2C%20quiero%20solicitar%20una%20cotización"
              className="whatsapp-btn"
              target="_blank"
              rel="noopener noreferrer"
              id="cta-whatsapp-btn"
            >
              <span aria-hidden="true"></span>
              Cotizar por WhatsApp
            </a>
            <a href="tel:+18091234567" className="btn btn-outline btn-lg" id="cta-call-btn">
               Llamar Ahora
            </a>
          </div>
        </div>
      </section>

      {/*  FOOTER  */}
      <footer className="footer" role="contentinfo">
        <div className="container">
          <div className="footer-grid">
            {/* Brand */}
            <div>
              <div className="footer-brand-name">Limpia<span>max</span></div>
              <p className="footer-brand-desc">
                Servicios profesionales de limpieza para hogares y empresas. Calidad,
                confianza y resultados garantizados desde 2016.
              </p>
              <div className="footer-socials">
                <a href="https://facebook.com" className="social-link" aria-label="Facebook" target="_blank" rel="noopener noreferrer"></a>
                <a href="https://instagram.com" className="social-link" aria-label="Instagram" target="_blank" rel="noopener noreferrer"></a>
                <a href="https://tiktok.com" className="social-link" aria-label="TikTok" target="_blank" rel="noopener noreferrer"></a>
                <a
                  href="https://wa.me/18091234567"
                  className="social-link"
                  aria-label="WhatsApp"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  
                </a>
              </div>
            </div>

            {/* Services */}
            <div>
              <h3 className="footer-col-title">Servicios</h3>
              <ul className="footer-links">
                <li><a href="#servicios">Limpieza Residencial</a></li>
                <li><a href="#servicios">Limpieza Comercial</a></li>
                <li><a href="#servicios">Post-Obra</a></li>
                <li><a href="#servicios">Limpieza Profunda</a></li>
                <li><a href="#servicios">Vidrios & Fachadas</a></li>
                <li><a href="#servicios">Desinfección</a></li>
              </ul>
            </div>

            {/* Company */}
            <div>
              <h3 className="footer-col-title">Empresa</h3>
              <ul className="footer-links">
                <li><a href="#nosotros">Sobre Nosotros</a></li>
                <li><a href="#proceso">Cómo Funciona</a></li>
                <li><a href="#testimonios">Testimonios</a></li>
                <li><a href="/pages/trabaja-con-nosotros">Trabaja con Nosotros</a></li>
                <li><a href="/policies/privacy-policy">Políticas de Privacidad</a></li>
              </ul>
            </div>

            {/* Contact */}
            <div>
              <h3 className="footer-col-title">Contacto</h3>
              <div className="footer-contact-item">
                <span className="footer-contact-icon"></span>
                <span>+1 (809) 123-4567</span>
              </div>
              <div className="footer-contact-item">
                <span className="footer-contact-icon"></span>
                <span>info@limpiamax.com</span>
              </div>
              <div className="footer-contact-item">
                <span className="footer-contact-icon"></span>
                <span>Santo Domingo, República Dominicana</span>
              </div>
              <div className="footer-contact-item">
                <span className="footer-contact-icon"></span>
                <span>Lun–Sáb: 7am – 8pm</span>
              </div>
            </div>
          </div>

          <div className="footer-bottom">
            <span>© {new Date().getFullYear()} Limpiamax. Todos los derechos reservados.</span>
            <span>
              Hecho con  por{' '}
              <a
                href="https://gahenax.com"
                target="_blank"
                rel="noopener noreferrer"
                style={{color: 'var(--teal)'}}
              >
                Gahenax
              </a>
            </span>
          </div>
        </div>
      </footer>
    </>
  );
}
