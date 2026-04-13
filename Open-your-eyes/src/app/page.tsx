import { TipJar } from '@/components/monetization/TipJar';
import { PatronWall } from '@/components/monetization/PatronWall';
import { EmbeddedProduct } from '@/components/monetization/EmbeddedProduct';

export default function Home() {
  return (
    <div className="min-h-screen bg-zinc-950 text-slate-100 font-sans selection:bg-emerald-500/30">

      {/* Hero Section para dar contexto visual */}
      <header className="relative pt-32 pb-20 px-4 text-center overflow-hidden">
        <div className="absolute top-0 inset-x-0 h-[500px] bg-gradient-to-b from-purple-500/10 via-emerald-500/5 to-transparent pointer-events-none" />
        <div className="relative z-10 max-w-3xl mx-auto space-y-6">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-xs font-medium text-emerald-400 uppercase tracking-widest mb-4 shadow-[0_0_15px_rgba(52,211,153,0.1)]">
            <span>Clúster 1: Creator Economy</span>
          </div>
          <h1 className="text-5xl md:text-7xl font-black tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-200 to-slate-500">
            Monetización <br /> Sin Fricciones.
          </h1>
          <p className="text-lg text-slate-400 max-w-xl mx-auto leading-relaxed">
            Ingeniería Inversa del ecosistema WordPress adaptada a Next.js. Módulos premium para Tip Jars, Patron Walls y Venta de Productos integrados.
          </p>
        </div>
      </header>

      <main className="relative z-20 max-w-6xl mx-auto px-4 pb-32 space-y-32">

        {/* Sección: Tip Jar */}
        <section className="scroll-mt-32">
          <div className="text-center mb-12 space-y-3">
            <h2 className="text-3xl font-bold">1. Tip Jar Dinámico</h2>
            <p className="text-slate-400">Pide apoyo directo al final de tus artículos de mayor valor.</p>
          </div>
          <TipJar authorName="Open your eyes" defaultAmount={5} />
        </section>

        {/* Sección: Embedded Product */}
        <section>
          <div className="text-center mb-12 space-y-3">
            <h2 className="text-3xl font-bold">2. Producto Integrado</h2>
            <p className="text-slate-400">Vende material exclusivo sin sacar al usuario del artículo que está leyendo.</p>
          </div>
          <EmbeddedProduct
            title="Dataset OEDA: Análisis de Hardware 2026"
            description="La base de datos completa con más de 5,000 benchmarks analizados en este artículo. Diseñada para investigadores y optimizadores de hardware."
            price={19.99}
            originalPrice={49.99}
            features={["Formato CSV + JSON estructurado", "Licencia Comercial Libre de Regalías", "Actualizaciones de por vida gratis"]}
            badge="Dataset Premium"
          />
        </section>

        {/* Sección: Patron Wall */}
        <section className="bg-white/5 border border-white/5 rounded-3xl p-4 md:p-8">
          <PatronWall />
        </section>

      </main>

    </div>
  );
}
