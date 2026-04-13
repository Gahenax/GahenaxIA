import Link from "next/link";
import Image from "next/image";

export default function Home() {
  return (
    <div className="min-h-screen selection:bg-emerald selection:text-white">
      {/* --- ELITE NAVIGATION --- */}
      <nav aria-label="Main navigation" className="navbar-elite fixed top-0 left-0 right-0 z-[100] h-20 flex items-center">
        <div className="container-elite w-full flex justify-between items-center">
          <Link href="/" className="flex items-center gap-2 group" aria-label="Gahenax AI Home">
            <span className="font-extrabold text-2xl tracking-tighter text-navy uppercase">
              Gahenax<span className="text-emerald group-hover:opacity-80 transition-opacity">AI</span>
            </span>
          </Link>
          
          <ul role="list" className="hidden md:flex items-center gap-12 text-[13px] font-bold text-navy/60 uppercase tracking-widest m-0 p-0 list-none">
            <li><Link href="#metodologia" className="hover:text-emerald transition-colors">Metodología</Link></li>
            <li><Link href="#servicios" className="hover:text-emerald transition-colors">Servicios</Link></li>
            <li><Link href="#casos" className="hover:text-emerald transition-colors">Casos</Link></li>
            <li><Link href="#contacto" className="bg-navy text-white px-6 py-3 rounded-lg hover:bg-emerald transition-all shadow-lg shadow-navy/10 active:scale-95">
              Solicitar Diagnóstico
            </Link></li>
          </ul>
        </div>
      </nav>

      {/* --- HERO ELITE (SPLIT 60/40) --- */}
      <section className="relative pt-32 pb-20 bg-white">
        <div className="container-elite">
          <div className="hero-split">
            {/* Left: Content */}
            <div className="animate-reveal">
              <span className="mono-tag">Infraestructura de Crecimiento // 2026</span>
              <h1 className="text-balance leading-[1.05]">
                Transformamos negocios en <span className="text-emerald">sistemas de crecimiento</span>
              </h1>
              <p className="text-lg md:text-xl mb-12 max-w-xl text-text-muted leading-relaxed">
                No diseñamos simples sitios. Construimos la ingeniería digital que permite a empresas de alto impacto automatizar su captación y escalar sin fricción.
              </p>
              <div className="flex flex-wrap gap-5">
                <Link href="#contacto" className="btn-primary">
                  Agenda tu diagnóstico estratégico
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
                </Link>
                <Link href="#servicios" className="btn-ghost group">
                  Ver capacidades
                  <span className="group-hover:translate-x-1 transition-transform">→</span>
                </Link>
              </div>
            </div>

            {/* Right: Premium Asset */}
            <div className="relative aspect-square w-full hidden lg:block animate-reveal [animation-delay:0.2s]">
              <div className="absolute inset-0 bg-emerald/5 rounded-[40px] -rotate-3 scale-95"></div>
              <div className="relative h-full w-full rounded-[40px] overflow-hidden border border-border shadow-2xl shadow-navy/5">
                <Image 
                  src="/nexus-hero.png" 
                  alt="Gahenax Infrastructure Asset" 
                  fill 
                  sizes="(max-width: 1024px) 100vw, 50vw"
                  className="object-cover"
                  priority
                />
              </div>
              {/* Floating Stat Card */}
              <div className="absolute -bottom-6 -left-6 bg-white p-6 rounded-2xl border border-border shadow-xl animate-reveal [animation-delay:1s]">
                <div className="text-emerald font-black text-2xl tracking-tighter">100%</div>
                <div className="text-[10px] font-bold uppercase tracking-widest text-navy/40">Saturación Operativa</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* --- METHODOLOGY (WATERMARK GRID) --- */}
      <section id="metodologia" className="section-padding bg-bg-secondary">
        <div className="container-elite">
          <div className="flex flex-col md:flex-row justify-between items-end mb-20 gap-8">
            <div className="max-w-xl">
              <span className="mono-tag !mb-4">Modus Operandi</span>
              <h2 className="tracking-tight text-navy">Fricción Cero. <span className="text-emerald">Control Total.</span></h2>
            </div>
            <p className="text-text-muted max-w-sm">
              Nuestra arquitectura se basa en la eliminación de silos operativos mediante auditoría y despliegue automatizado.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              { id: '01', title: 'Auditoría Táctica', desc: 'Analizamos fugas de leads y cuellos de botella técnicos en tu infraestructura actual.', icon: 'A' },
              { id: '02', title: 'Diseño de Control', desc: 'Desplegamos activos digitales conectados a CRM y flujos de automatización de grado comercial.', icon: 'D' },
              { id: '03', title: 'Escalado Activo', desc: 'Optimizamos la conversión mediante datos empíricos y campañas orientadas 100% a ROI.', icon: 'E' }
            ].map((step) => (
              <div key={step.id} className="card-nexus group">
                <div className="watermark-number transition-all group-hover:scale-110 group-hover:text-emerald">{step.id}</div>
                <div className="relative z-10">
                  <div className="w-12 h-12 rounded-xl bg-navy text-white font-bold flex items-center justify-center mb-8 shadow-lg shadow-navy/10">
                    {step.icon}
                  </div>
                  <h3 className="mb-4 text-navy font-extrabold">{step.title}</h3>
                  <p className="text-sm leading-relaxed">{step.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* --- SERVICES (CAPABILITIES) --- */}
      <section id="servicios" className="section-padding bg-white">
        <div className="container-elite">
          <div className="grid lg:grid-cols-2 gap-24 items-center">
            <div className="relative">
               <div className="absolute -top-12 -left-12 w-64 h-64 bg-emerald/5 rounded-full blur-3xl"></div>
               <div className="relative grid grid-cols-2 gap-4">
                  <div className="space-y-4 pt-12">
                    <div className="bg-bg-smoke p-8 rounded-3xl border border-border hover:border-emerald transition-colors">
                      <div className="font-bold text-navy mb-2">Automations</div>
                      <div className="text-[10px] text-text-muted uppercase tracking-widest italic">Node.js // n8n</div>
                    </div>
                    <div className="bg-navy p-8 rounded-3xl text-white">
                      <div className="font-bold mb-2 text-emerald">UI Development</div>
                      <div className="text-[10px] text-white/40 uppercase tracking-widest italic">Next.js // React 19</div>
                    </div>
                  </div>
                  <div className="space-y-4">
                    <div className="bg-bg-smoke p-8 rounded-3xl border border-border">
                      <div className="font-bold text-navy mb-2">Scalability</div>
                      <div className="text-[10px] text-text-muted uppercase tracking-widest italic">Global Edge Network</div>
                    </div>
                    <div className="bg-emerald p-8 rounded-3xl text-white">
                      <div className="font-bold mb-2">Security</div>
                      <div className="text-[10px] text-white/60 uppercase tracking-widest italic">Verified Red-Teaming</div>
                    </div>
                  </div>
               </div>
            </div>

            <div>
              <span className="mono-tag">Capacidades Digitales</span>
              <h2 className="mb-8 leading-tight">Infraestructura diseñada para la <span className="text-emerald">nueva economía</span>.</h2>
              <div className="grid gap-6">
                {[
                  { t: 'Landing Pages de Conversión', d: 'Despliegues estáticos optimizados para SEO y velocidad extrema.' },
                  { t: 'Automatización de Ventas', d: 'Integración de CRMs y flujos de nutrición de leads sin intervención humana.' },
                  { t: 'Consultoría de Escalado', d: 'Análisis de datos para detectar oportunidades reales de crecimiento vertical.' }
                ].map((s) => (
                  <div key={s.t} className="flex gap-5">
                    <div className="mt-1.5 w-5 h-5 rounded-full bg-emerald/10 flex items-center justify-center flex-shrink-0">
                      <div className="w-2 h-2 rounded-full bg-emerald"></div>
                    </div>
                    <div>
                      <h4 className="font-bold text-navy mb-1">{s.t}</h4>
                      <p className="text-sm text-text-muted">{s.d}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* --- SUCCESS CASES --- */}
      <section id="casos" className="section-padding section-navy">
        <div className="container-elite">
          <div className="max-w-2xl mb-24">
            <span className="mono-tag !text-emerald">Casos de Éxito</span>
            <h2 className="text-white !text-6xl font-black mb-8">Sistemas desplegados.</h2>
            <p className="text-white/60 text-lg italic tracking-tight">
              "No vendemos promesas. Desplegamos arquitectura operacional que genera beneficios desde el día uno."
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-10">
            {[
              { name: 'LimpiaMAX', link: 'https://limpiamaxweb.com', type: 'Booking & Payments' },
              { name: 'Mudanza Fácil', link: 'https://mudanzafacilbcn.com', type: 'Logistics Infrastructure' }
            ].map((p) => (
              <div key={p.name} className="group p-10 bg-white/5 border border-white/10 rounded-[32px] hover:bg-white/10 transition-all hover:border-emerald/50">
                <div className="flex justify-between items-start mb-20 md:mb-40">
                  <div>
                    <h3 className="text-white text-3xl font-black mb-2">{p.name}</h3>
                    <p className="text-emerald font-bold text-xs uppercase tracking-widest">{p.type}</p>
                  </div>
                  <Link href={p.link} target="_blank" rel="noopener noreferrer" className="w-14 h-14 rounded-full border border-white/20 flex items-center justify-center group-hover:bg-emerald group-hover:border-emerald transition-all active:scale-90">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M7 17L17 7M17 7H7M17 7V17"/></svg>
                  </Link>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 rounded-full bg-emerald animate-pulse"></div>
                  <div className="text-[10px] font-bold tracking-[0.2em] text-white/30 uppercase italic">Active Ecosystem</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* --- CTA FINAL --- */}
      <section id="contacto" className="section-padding bg-white text-center">
        <div className="container-elite max-w-4xl">
          <h2 className="text-balance md:!text-8xl !font-black leading-[0.9] mb-12">Lleva tu negocio al <span className="text-emerald">siguiente nivel.</span></h2>
          <p className="text-xl text-text-muted mb-16 max-w-2xl mx-auto italic">
            Hablemos de cómo transformar tu operación digital en una máquina de crecimiento estratégica.
          </p>
          <div className="flex flex-col items-center gap-8">
            <Link href="mailto:jorge@gahenax.ai" className="btn-primary text-xl px-16 py-8 shadow-2xl shadow-emerald/20">
              Solicitar diagnóstico estratégico
            </Link>
            <div className="text-[11px] font-black text-navy/30 uppercase tracking-[0.5em]">
              Soberanía Digital // Control Total // 2026
            </div>
          </div>
        </div>
      </section>

      <footer className="py-12 border-t border-border bg-bg-secondary">
        <div className="container-elite flex flex-col md:flex-row justify-between items-center gap-6">
          <div className="font-extrabold text-navy text-lg">GAHENAX AI</div>
          <div className="text-[10px] font-bold text-text-muted tracking-widest uppercase">
            © 2026 Gahenax AI Solutions // Barcelona // High-Growth Infrastructure
          </div>
        </div>
      </footer>
    </div>
  );
}
