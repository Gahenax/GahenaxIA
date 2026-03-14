'use client';

import Image from 'next/image';
import { Phone, MessageCircle, MapPin, Menu, X, Star, Check, Send } from 'lucide-react';
import { useState, FormEvent } from 'react';

export default function Home() {
  const [menuOpen, setMenuOpen] = useState(false);
  const [formStatus, setFormStatus] = useState<'idle' | 'sending' | 'success' | 'error'>('idle');

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setFormStatus('sending');
    const form = e.currentTarget;
    const data = new FormData(form);
    try {
      const res = await fetch('https://formsubmit.co/ajax/limpiamax@gmail.com', {
        method: 'POST',
        headers: { Accept: 'application/json' },
        body: data,
      });
      if (res.ok) {
        setFormStatus('success');
        form.reset();
      } else {
        setFormStatus('error');
      }
    } catch {
      setFormStatus('error');
    }
  }

  return (
    <div className="min-h-screen bg-background text-foreground selection:bg-primary/10">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 z-50 bg-card/95 backdrop-blur-md border-b border-border transition-all duration-300">
        <div className="container mx-auto px-6 h-16 flex items-center justify-between">
          <a href="#" className="flex items-center gap-1 hover:opacity-90 transition-opacity">
            <span className="text-2xl font-bold text-primary">Limpia</span>
            <span className="text-2xl font-bold text-accent">MAX</span>
          </a>

          <nav className="hidden md:flex items-center gap-8">
            <a href="#servicios" className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors">
              Servicios
            </a>
            <a href="#contacto" className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors">
              Contacto
            </a>
            <a href="tel:+34674571497" className="flex items-center gap-2 text-sm font-medium text-primary hover:text-primary/80 transition-colors">
              <Phone className="w-4 h-4" />
              +34 674 571 497
            </a>
            <a
              href="https://wa.me/34674571497"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-4 py-2 rounded-full bg-success text-success-foreground text-sm font-semibold hover:opacity-90 transition-all active:scale-[0.98] shadow-sm"
            >
              <MessageCircle className="w-4 h-4" />
              WhatsApp
            </a>
          </nav>

          <button
            className="md:hidden p-2 text-primary hover:bg-primary/5 rounded-full transition-colors"
            aria-label="Toggle menu"
            aria-expanded={menuOpen}
            onClick={() => setMenuOpen((v) => !v)}
          >
            {menuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>

        {/* Mobile menu */}
        {menuOpen && (
          <div className="md:hidden bg-card border-t border-border px-6 py-4 flex flex-col gap-4 animate-fade-in-up">
            <a href="#servicios" onClick={() => setMenuOpen(false)} className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors">
              Servicios
            </a>
            <a href="#contacto" onClick={() => setMenuOpen(false)} className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors">
              Contacto
            </a>
            <a href="tel:+34674571497" className="flex items-center gap-2 text-sm font-medium text-primary">
              <Phone className="w-4 h-4" />
              +34 674 571 497
            </a>
            <a
              href="https://wa.me/34674571497"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-4 py-2 rounded-full bg-success text-success-foreground text-sm font-semibold w-fit"
            >
              <MessageCircle className="w-4 h-4" />
              WhatsApp
            </a>
          </div>
        )}
      </header>

      <main>
        {/* Hero Section */}
        <section className="relative min-h-[90vh] flex items-center pt-20 bg-card overflow-hidden">
          <div className="container mx-auto px-6 grid lg:grid-cols-2 gap-12 items-center">
            <div className="animate-fade-in-up">
              <div className="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 mb-4 bg-success/10 text-success border-success/20 hover:bg-success/20 font-medium">
                ✨ Limpieza Profesional en Barcelona
              </div>
              <h1 className="text-5xl lg:text-7xl font-bold text-primary leading-[1.1] mb-6 tracking-tight">
                Limpiezas de <span className="text-accent">casas</span> y sofás.
              </h1>
              <p className="text-xl text-muted-foreground mb-8 max-w-md leading-relaxed">
                Recupera tu tiempo. Resultados impecables con precios transparentes desde <span className="font-bold text-primary">€9,99</span>.
              </p>

              <div className="flex flex-col sm:flex-row gap-4">
                <a
                  href="#servicios"
                  className="inline-flex items-center justify-center px-8 py-4 bg-accent text-accent-foreground rounded-full font-bold text-lg shadow-orange-glow hover:shadow-elegant-xl transition-all active:scale-[0.98] hover:-translate-y-0.5"
                >
                  Reserva tu limpieza ahora
                </a>
                <div className="flex items-center gap-3 px-6 py-4 border border-border rounded-full bg-card shadow-sm">
                  <div className="w-2 h-2 bg-success rounded-full animate-pulse" />
                  <span className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                    <MapPin className="w-4 h-4" /> Disponible hoy en Barcelona
                  </span>
                </div>
              </div>
            </div>

            <div className="relative animate-scale-in">
              <div className="aspect-square rounded-[2rem] overflow-hidden shadow-elegant-xl border-[12px] border-background bg-muted">
                <Image
                  src="https://images.unsplash.com/photo-1581578731548-c64695cc6952?auto=format&fit=crop&q=80&w=1200"
                  width={1200}
                  height={1200}
                  className="w-full h-full object-cover transition-transform duration-700 hover:scale-105"
                  alt="Interior de hogar limpio y moderno"
                  priority
                />
              </div>

              {/* Review Badge */}
              <div className="absolute -bottom-6 -left-6 bg-card p-5 rounded-2xl shadow-elegant-lg border border-border max-w-[220px] animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
                <div className="flex gap-1 mb-2">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="w-4 h-4 fill-accent text-accent" />
                  ))}
                </div>
                <p className="text-sm font-bold text-primary">
                  4.9/5 de 2,000+ clientes en Barcelona
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Services Section */}
        <section id="servicios" className="py-24 bg-background">
          <div className="container mx-auto px-6">
            <div className="text-center mb-16">
              <h2 className="text-4xl lg:text-5xl font-bold text-primary mb-4 tracking-tight">Nuestros Servicios</h2>
              <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                Precios transparentes y sin sorpresas. Selecciona los extras que necesites y calcula tu presupuesto al instante.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {/* Básica */}
              <div className="rounded-2xl border bg-card text-card-foreground overflow-hidden border-border shadow-elegant hover:shadow-elegant-lg transition-all duration-300 h-full flex flex-col group hover:-translate-y-1">
                <div className="h-56 overflow-hidden relative bg-muted">
                  <Image
                    src="https://images.unsplash.com/photo-1584622650111-993a426fbf0a?auto=format&fit=crop&q=80&w=800"
                    width={800}
                    height={450}
                    alt="Limpieza Básica"
                    className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
                    loading="lazy"
                  />
                </div>
                <div className="p-8 flex flex-col flex-1">
                  <h3 className="text-2xl font-bold text-primary mb-2">Limpieza de Casa (Básica)</h3>
                  <p className="text-muted-foreground mb-6 leading-relaxed">Limpieza estándar para mantener tu hogar impecable. Incluye 2 habitaciones.</p>

                  <div className="flex items-baseline gap-2 mb-8 pb-8 border-b border-border/50">
                    <span className="text-4xl font-bold text-primary tabular-nums">€9.99</span>
                    <span className="text-sm font-medium text-muted-foreground">/ 2 habitaciones</span>
                  </div>

                  <div className="mt-auto">
                    <a href="#contacto" className="block w-full py-4 text-center bg-accent text-accent-foreground rounded-xl font-bold hover:opacity-90 transition-all shadow-orange-glow active:scale-[0.98]">
                      Reservar — €9.99
                    </a>
                  </div>
                </div>
              </div>

              {/* Profunda */}
              <div className="rounded-2xl border bg-card text-card-foreground overflow-hidden border-primary/20 shadow-elegant-lg hover:shadow-elegant-xl transition-all duration-300 h-full flex flex-col group hover:-translate-y-1 relative">
                <div className="absolute top-0 inset-x-0 h-1 bg-gradient-to-r from-primary to-accent z-10" />
                <div className="h-56 overflow-hidden relative bg-muted">
                  <Image
                    src="https://images.unsplash.com/photo-1527515637462-cff94eebd21d?auto=format&fit=crop&q=80&w=800"
                    width={800}
                    height={450}
                    alt="Limpieza Profunda"
                    className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
                    loading="lazy"
                  />
                  <div className="absolute top-4 right-4 bg-primary text-primary-foreground px-3 py-1 rounded-full text-xs font-bold tracking-wide uppercase shadow-lg">Más popular</div>
                </div>
                <div className="p-8 flex flex-col flex-1">
                  <h3 className="text-2xl font-bold text-primary mb-2">Limpieza Profunda de Casa</h3>
                  <p className="text-muted-foreground mb-6 leading-relaxed">Una limpieza a fondo para dejar tu hogar como nuevo. 3 horas de servicio profesional.</p>

                  <div className="flex items-baseline gap-2 mb-6 pb-6 border-b border-border/50">
                    <span className="text-4xl font-bold text-primary tabular-nums">€39.99</span>
                    <span className="text-sm font-medium text-muted-foreground">/ 3 horas</span>
                  </div>

                  <ul className="space-y-3 mb-8">
                    {['Limpieza de hornos', 'Limpieza de ventanas', '3 habitaciones', 'Sala comedor', '1 baño', 'Cocina'].map((item) => (
                      <li key={item} className="flex items-start gap-3 text-sm text-foreground font-medium">
                        <Check className="w-5 h-5 text-success shrink-0" /> {item}
                      </li>
                    ))}
                  </ul>

                  <div className="mt-auto">
                    <a href="#contacto" className="block w-full py-4 text-center bg-primary text-primary-foreground rounded-xl font-bold hover:bg-primary/90 transition-all shadow-md active:scale-[0.98]">
                      Reservar — €39.99
                    </a>
                  </div>
                </div>
              </div>

              {/* Fin de Obra */}
              <div className="rounded-2xl border bg-card text-card-foreground overflow-hidden border-border shadow-elegant hover:shadow-elegant-lg transition-all duration-300 h-full flex flex-col group hover:-translate-y-1">
                <div className="h-56 overflow-hidden relative bg-muted">
                  <Image
                    src="https://images.unsplash.com/photo-1558618666-fcd25c85f82e?auto=format&fit=crop&q=80&w=800"
                    width={800}
                    height={450}
                    alt="Limpieza Fin de Obra"
                    className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
                    loading="lazy"
                  />
                  <div className="absolute top-4 right-4 bg-accent text-accent-foreground px-3 py-1 rounded-full text-xs font-bold tracking-wide shadow-lg">Especializada</div>
                </div>
                <div className="p-8 flex flex-col flex-1">
                  <h3 className="text-2xl font-bold text-primary mb-2">Limpieza Fin de Obra</h3>
                  <p className="text-muted-foreground mb-6 leading-relaxed">Todo lo de limpieza profunda más servicios especializados post-obra.</p>

                  <div className="flex items-baseline gap-2 mb-6 pb-6 border-b border-border/50">
                    <span className="text-4xl font-bold text-primary tabular-nums">€49.99</span>
                    <span className="text-sm font-medium text-muted-foreground">/ 3 horas</span>
                  </div>

                  <ul className="space-y-3 mb-8">
                    {['Todo lo de Limpieza Profunda', 'Limpieza de paredes y polvo', 'Despegar pintura del suelo', 'Tirar basuras'].map((item) => (
                      <li key={item} className="flex items-start gap-3 text-sm text-foreground font-medium">
                        <Check className="w-5 h-5 text-success shrink-0" /> {item}
                      </li>
                    ))}
                  </ul>

                  <div className="mt-auto">
                    <a href="#contacto" className="block w-full py-4 text-center bg-accent text-accent-foreground rounded-xl font-bold hover:opacity-90 transition-all shadow-orange-glow active:scale-[0.98]">
                      Reservar — €49.99
                    </a>
                  </div>
                </div>
              </div>

              {/* Extras (Sofás, Alfombras, Colchones) */}
              <div className="rounded-2xl border bg-card overflow-hidden border-border shadow-elegant hover:shadow-elegant-lg transition-all flex flex-col group col-span-1 md:col-span-2 lg:col-span-3 lg:flex-row mt-4">
                <div className="p-8 flex-1 border-r border-border">
                  <h3 className="text-xl font-bold text-primary mb-2">❄️ Sofás</h3>
                  <p className="text-sm text-muted-foreground mb-4">Tapicería impecable al instante.</p>
                  <ul className="space-y-2 text-sm font-medium text-foreground">
                    <li className="flex justify-between items-center py-2 border-b border-border/30"><span>4 Plazas</span> <span className="font-bold">€100</span></li>
                    <li className="flex justify-between items-center py-2 border-b border-border/30"><span>3 Plazas</span> <span className="font-bold">€85</span></li>
                    <li className="flex justify-between items-center py-2"><span>2 Plazas</span> <span className="font-bold">€55</span></li>
                  </ul>
                </div>
                <div className="p-8 flex-1 border-r border-border">
                  <h3 className="text-xl font-bold text-primary mb-2">✨ Alfombras</h3>
                  <p className="text-sm text-muted-foreground mb-4">Elimina olores y manchas.</p>
                  <ul className="space-y-2 text-sm font-medium text-foreground">
                    <li className="flex justify-between items-center py-2 border-b border-border/30"><span>2 a 4 metros</span> <span className="font-bold">€40</span></li>
                    <li className="flex justify-between items-center py-2"><span>4 a 7 metros</span> <span className="font-bold">€70</span></li>
                  </ul>
                </div>
                <div className="p-8 flex-1 bg-primary/5">
                  <h3 className="text-xl font-bold text-primary mb-2 flex items-center gap-2">🔥 Colchones <span className="text-[10px] bg-accent text-white px-2 py-0.5 rounded-full uppercase tracking-wider">Oferta</span></h3>
                  <p className="text-sm text-muted-foreground mb-4">Ambas caras. Adiós ácaros.</p>
                  <ul className="space-y-2 text-sm font-medium text-foreground">
                    <li className="flex justify-between items-center py-2 border-b border-primary/10"><span>160×190</span> <div className="flex gap-2"><span className="line-through text-muted-foreground">€75</span><span className="font-bold text-accent">€65</span></div></li>
                    <li className="flex justify-between items-center py-2"><span>140×190</span> <div className="flex gap-2"><span className="line-through text-muted-foreground">€55</span><span className="font-bold text-accent">€45</span></div></li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Contact Section */}
        <section id="contacto" className="py-24 bg-card border-t border-border">
          <div className="container mx-auto px-6">
            <div className="grid lg:grid-cols-2 gap-16 items-center max-w-6xl mx-auto">
              <div>
                <h2 className="text-4xl lg:text-5xl font-bold text-primary mb-6 tracking-tight">Solicita tu presupuesto gratuito</h2>
                <p className="text-muted-foreground mb-8 text-xl leading-relaxed">
                  Déjanos tus datos y te enviaremos un presupuesto personalizado en menos de 1 hora. Sin compromiso.
                </p>

                <div className="space-y-6">
                  <div className="flex items-center gap-5 p-6 rounded-2xl bg-background border border-border shadow-sm hover:shadow-md transition-shadow">
                    <div className="w-14 h-14 rounded-xl bg-primary/10 flex items-center justify-center shrink-0">
                      <Phone className="w-6 h-6 text-primary" />
                    </div>
                    <div>
                      <p className="text-sm font-bold text-muted-foreground uppercase tracking-wider mb-1">Teléfono Directo</p>
                      <a href="tel:+34674571497" className="text-2xl font-bold text-primary hover:text-accent transition-colors">+34 674 571 497</a>
                    </div>
                  </div>

                  <a
                    href="https://wa.me/34674571497"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-5 p-6 rounded-2xl bg-success/5 border border-success/20 hover:bg-success/10 transition-all group"
                  >
                    <div className="w-14 h-14 rounded-xl bg-success/20 flex items-center justify-center shrink-0 group-hover:scale-110 transition-transform">
                      <MessageCircle className="w-6 h-6 text-success" />
                    </div>
                    <div>
                      <p className="text-sm font-bold text-success/80 uppercase tracking-wider mb-1">Respuesta Rápida</p>
                      <span className="text-xl font-bold text-foreground">Escríbenos por WhatsApp</span>
                    </div>
                  </a>
                </div>

                <p className="mt-8 text-sm font-medium text-muted-foreground flex items-center gap-2">
                  <Star className="w-4 h-4 fill-accent text-accent" /> 98.4% de satisfacción en limpiezas en Barcelona
                </p>
              </div>

              <div>
                {formStatus === 'success' ? (
                  <div className="bg-background p-10 rounded-3xl border border-success/30 shadow-elegant-xl text-center space-y-4">
                    <div className="w-16 h-16 rounded-full bg-success/10 flex items-center justify-center mx-auto">
                      <Check className="w-8 h-8 text-success" />
                    </div>
                    <h3 className="text-2xl font-bold text-primary">¡Solicitud enviada!</h3>
                    <p className="text-muted-foreground">Te responderemos con tu cotización en menos de 1 hora.</p>
                    <button
                      onClick={() => setFormStatus('idle')}
                      className="text-sm font-medium text-accent hover:underline"
                    >
                      Enviar otra solicitud
                    </button>
                  </div>
                ) : (
                  <form onSubmit={handleSubmit} className="bg-background p-8 md:p-10 rounded-3xl border border-border shadow-elegant-xl space-y-6">
                    <input type="hidden" name="_captcha" value="false" />
                    <input type="hidden" name="_subject" value="Nueva solicitud de presupuesto - LimpiaMAX" />
                    <div className="space-y-2">
                      <label className="text-sm font-semibold text-primary" htmlFor="name">Nombre Completo</label>
                      <input
                        className="flex h-12 w-full rounded-xl border border-input bg-card px-4 py-2 text-base transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent/50 focus-visible:border-accent"
                        id="name"
                        name="name"
                        placeholder="Ej. María García"
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-semibold text-primary" htmlFor="email">Correo Electrónico</label>
                      <input
                        type="email"
                        className="flex h-12 w-full rounded-xl border border-input bg-card px-4 py-2 text-base transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent/50 focus-visible:border-accent"
                        id="email"
                        name="email"
                        placeholder="tu@email.com"
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-semibold text-primary" htmlFor="phone">Teléfono</label>
                      <input
                        type="tel"
                        className="flex h-12 w-full rounded-xl border border-input bg-card px-4 py-2 text-base transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent/50 focus-visible:border-accent"
                        id="phone"
                        name="phone"
                        placeholder="+34 600 000 000"
                        required
                      />
                    </div>
                    {formStatus === 'error' && (
                      <p className="text-sm text-red-500 font-medium">
                        Hubo un error al enviar. Por favor llámanos directamente.
                      </p>
                    )}
                    <button
                      type="submit"
                      disabled={formStatus === 'sending'}
                      className="w-full py-4 flex items-center justify-center gap-2 bg-accent text-accent-foreground rounded-xl font-bold text-lg shadow-orange-glow hover:opacity-90 transition-all active:scale-[0.98] mt-4 disabled:opacity-70 disabled:cursor-not-allowed"
                    >
                      <Send className="w-5 h-5" />
                      {formStatus === 'sending' ? 'Enviando...' : 'Solicitar Presupuesto'}
                    </button>
                    <p className="text-sm font-medium text-center text-muted-foreground">
                      Te responderemos con tu cotización en menos de 1 hora.
                    </p>
                  </form>
                )}
              </div>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-primary py-16 border-t-[12px] border-accent">
        <div className="container mx-auto px-6">
          <div className="flex flex-col md:flex-row items-center justify-between gap-8">
            <div className="text-center md:text-left">
              <span className="text-3xl font-bold text-primary-foreground tracking-tight">
                Limpia<span className="text-accent">MAX</span>
              </span>
              <p className="text-primary-foreground/70 text-base mt-2 font-medium">
                Tu hogar, en su versión MAX.
              </p>
            </div>

            <div className="flex flex-col sm:flex-row items-center gap-8 text-primary-foreground/90 font-medium">
              <a href="tel:+34674571497" className="flex items-center gap-2 hover:text-accent transition-colors">
                <Phone className="w-5 h-5" />
                +34 674 571 497
              </a>
              <span className="flex items-center gap-2">
                <MapPin className="w-5 h-5" />
                Barcelona, España
              </span>
            </div>
          </div>

          <div className="border-t border-primary-foreground/10 mt-12 pt-8 text-center text-sm text-primary-foreground/50 font-medium">
            © {new Date().getFullYear()} Limpia MAX. Todos los derechos reservados.
          </div>
        </div>
      </footer>
    </div>
  );
}
