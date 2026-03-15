'use client';

import Image from 'next/image';
import { Phone, MessageCircle, MapPin, Menu, X, Check, Send } from 'lucide-react';
import { useState, FormEvent } from 'react';

function SelectionItem({
  label,
  price,
  checked,
  onChange,
  originalPrice,
}: {
  label: string;
  price: string;
  checked: boolean;
  onChange: () => void;
  originalPrice?: string;
}) {
  return (
    <button
      type="button"
      onClick={onChange}
      className="flex items-center justify-between w-full py-2.5 gap-3 text-left hover:bg-gray-50 rounded-lg px-1 -mx-1 transition-colors"
    >
      <div className="flex items-center gap-3">
        <div
          className={`w-5 h-5 rounded-full border-2 flex items-center justify-center shrink-0 transition-colors ${
            checked ? 'bg-[#1e3a5f] border-[#1e3a5f]' : 'border-gray-300'
          }`}
        >
          {checked && <Check className="w-3 h-3 text-white" strokeWidth={3} />}
        </div>
        <span className={`text-sm ${checked ? 'text-gray-800 font-medium' : 'text-gray-500'}`}>
          {label}
        </span>
      </div>
      <div className="flex items-center gap-2 shrink-0">
        {originalPrice && (
          <span className="text-sm line-through text-gray-400">{originalPrice}</span>
        )}
        <span className="text-sm font-semibold text-emerald-600">{price}</span>
      </div>
    </button>
  );
}

export default function Home() {
  const [menuOpen, setMenuOpen] = useState(false);
  const [formStatus, setFormStatus] = useState<'idle' | 'sending' | 'success' | 'error'>('idle');

  const [basicaExtras, setBasicaExtras] = useState({
    habitacion: true,
    mascotas: true,
    aspiradora: false,
    desplazamiento: false,
    productos: false,
  });

  const [profundaExtras, setProfundaExtras] = useState({
    bano: true,
    habitacion: true,
    platos: true,
    balcon: true,
    planchar: true,
    moho: false,
  });

  const [sofasSelected, setSofasSelected] = useState({
    s4plazas: true,
    s3plazas: true,
    s2plazas: true,
    sillasComedor: false,
    sillasReclinables: false,
  });

  const [alfombraSelected, setAlfombraSelected] = useState<string | null>(null);
  const [colchonSelected, setColchonSelected] = useState<string | null>(null);

  const basicaBase = 9.99;
  const basicaExtrasMap = {
    habitacion: 6.99,
    mascotas: 1.99,
    aspiradora: 2.99,
    desplazamiento: 4.99,
    productos: 4.99,
  };
  const basicaTotal =
    basicaBase +
    (Object.keys(basicaExtras) as Array<keyof typeof basicaExtras>).reduce(
      (sum, k) => (basicaExtras[k] ? sum + basicaExtrasMap[k] : sum),
      0
    );

  const profundaBase = 39.99;
  const profundaExtrasMap = {
    bano: 6.99,
    habitacion: 5.99,
    platos: 4.99,
    balcon: 5.99,
    planchar: 19.99,
    moho: 8.99,
  };
  const profundaTotal =
    profundaBase +
    (Object.keys(profundaExtras) as Array<keyof typeof profundaExtras>).reduce(
      (sum, k) => (profundaExtras[k] ? sum + profundaExtrasMap[k] : sum),
      0
    );

  const sofasMap = {
    s4plazas: 100,
    s3plazas: 85,
    s2plazas: 55,
    sillasComedor: 8,
    sillasReclinables: 20,
  };
  const sofasTotal = (Object.keys(sofasSelected) as Array<keyof typeof sofasSelected>).reduce(
    (sum, k) => (sofasSelected[k] ? sum + sofasMap[k] : sum),
    0
  );

  const alfombraPrice = alfombraSelected === '2a4' ? 40 : alfombraSelected === '4a7' ? 70 : null;
  const colchonPrice = colchonSelected === '160' ? 65 : colchonSelected === '140' ? 45 : null;

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
    <div className="min-h-screen bg-white text-gray-900">
      {/* Top accent bar */}
      <div className="h-1.5 bg-red-800 w-full" />

      {/* Header */}
      <header className="sticky top-0 z-50 bg-white border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <a href="#" className="flex items-center hover:opacity-90 transition-opacity">
            <span className="text-2xl font-bold text-[#1e3a5f]">Limpia</span>
            <span className="text-2xl font-bold text-orange-500">MAX</span>
          </a>

          <nav className="hidden md:flex items-center gap-8">
            <a
              href="#servicios"
              className="text-sm font-medium text-gray-500 hover:text-[#1e3a5f] transition-colors"
            >
              Servicios
            </a>
            <a
              href="#contacto"
              className="text-sm font-medium text-gray-500 hover:text-[#1e3a5f] transition-colors"
            >
              Contacto
            </a>
            <a
              href="tel:+34674571497"
              className="flex items-center gap-2 text-sm font-medium text-gray-500 hover:text-[#1e3a5f] transition-colors"
            >
              <Phone className="w-4 h-4" />
              +34 674 571 497
            </a>
            <a
              href="https://wa.me/34674571497"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-5 py-2.5 rounded-full bg-emerald-500 text-white text-sm font-semibold hover:bg-emerald-600 transition-all shadow-sm"
            >
              <MessageCircle className="w-4 h-4" />
              WhatsApp
            </a>
          </nav>

          <button
            className="md:hidden p-2 text-[#1e3a5f] rounded-full hover:bg-gray-50 transition-colors"
            aria-label="Toggle menu"
            onClick={() => setMenuOpen((v) => !v)}
          >
            {menuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>

        {menuOpen && (
          <div className="md:hidden bg-white border-t border-gray-100 px-6 py-4 flex flex-col gap-4">
            <a
              href="#servicios"
              onClick={() => setMenuOpen(false)}
              className="text-sm font-medium text-gray-500"
            >
              Servicios
            </a>
            <a
              href="#contacto"
              onClick={() => setMenuOpen(false)}
              className="text-sm font-medium text-gray-500"
            >
              Contacto
            </a>
            <a
              href="tel:+34674571497"
              className="flex items-center gap-2 text-sm font-medium text-[#1e3a5f]"
            >
              <Phone className="w-4 h-4" /> +34 674 571 497
            </a>
            <a
              href="https://wa.me/34674571497"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-4 py-2 rounded-full bg-emerald-500 text-white text-sm font-semibold w-fit"
            >
              <MessageCircle className="w-4 h-4" /> WhatsApp
            </a>
          </div>
        )}
      </header>

      <main>
        {/* Hero Section */}
        <section className="bg-white overflow-hidden">
          <div className="max-w-7xl mx-auto grid lg:grid-cols-2 min-h-[580px]">
            <div className="flex flex-col justify-center px-6 py-16 lg:py-24 lg:pr-10">
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-700 text-sm font-medium mb-6 w-fit">
                ✨ Limpieza Profesional en Barcelona
              </div>
              <h1 className="text-5xl lg:text-6xl font-extrabold text-[#1e3a5f] leading-tight mb-6">
                Limpiezas de{' '}
                <span className="text-orange-500">casas</span>
                <br />y sofás.
              </h1>
              <p className="text-lg text-gray-500 mb-8 max-w-md leading-relaxed">
                Recupera tu tiempo. Resultados impecables con precios transparentes desde{' '}
                <span className="font-bold text-gray-700">€9,99</span>.
              </p>
              <div className="flex flex-col sm:flex-row gap-4">
                <a
                  href="#servicios"
                  className="inline-flex items-center justify-center px-8 py-4 bg-orange-500 text-white rounded-full font-bold text-base shadow-lg hover:bg-orange-600 transition-all active:scale-[0.98]"
                >
                  Reserva tu limpieza ahora
                </a>
                <div className="flex items-center gap-3 px-6 py-4 border border-gray-200 rounded-full bg-white shadow-sm">
                  <div className="w-2 h-2 bg-emerald-500 rounded-full" />
                  <span className="text-sm font-medium text-gray-500 flex items-center gap-1.5">
                    <MapPin className="w-4 h-4" /> Disponible hoy en Barcelona
                  </span>
                </div>
              </div>
            </div>

            <div className="relative hidden lg:block min-h-[500px]">
              <Image
                src="https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?auto=format&fit=crop&q=80&w=1200"
                fill
                className="object-cover rounded-l-[2rem]"
                alt="Interior de hogar limpio y moderno"
                priority
              />
            </div>
          </div>
        </section>

        {/* Services Section */}
        <section id="servicios" className="py-20 bg-slate-50">
          <div className="max-w-7xl mx-auto px-6">
            <div className="text-center mb-14">
              <h2 className="text-4xl lg:text-5xl font-extrabold text-[#1e3a5f] mb-4">
                Nuestros Servicios
              </h2>
              <p className="text-lg text-gray-500 max-w-2xl mx-auto">
                Precios transparentes y sin sorpresas. Selecciona los extras que necesites y calcula
                tu presupuesto al instante.
              </p>
            </div>

            {/* House cleaning cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {/* Básica */}
              <div className="bg-white rounded-2xl overflow-hidden shadow-sm border border-gray-100 flex flex-col">
                <div className="h-52 overflow-hidden">
                  <Image
                    src="https://images.unsplash.com/photo-1584622650111-993a426fbf0a?auto=format&fit=crop&q=80&w=800"
                    width={800}
                    height={450}
                    alt="Limpieza de Casa Básica"
                    className="w-full h-full object-cover"
                    loading="lazy"
                  />
                </div>
                <div className="p-6 flex flex-col flex-1">
                  <h3 className="text-lg font-bold text-[#1e3a5f] mb-1">
                    Limpieza de Casa (Básica)
                  </h3>
                  <p className="text-sm text-gray-500 mb-4">
                    Limpieza estándar para mantener tu hogar impecable. Incluye 2 habitaciones.
                  </p>
                  <div className="flex items-baseline gap-2 mb-5">
                    <span className="text-3xl font-extrabold text-[#1e3a5f]">
                      €{basicaTotal.toFixed(2)}
                    </span>
                    <span className="text-sm text-gray-400">2 habitaciones</span>
                  </div>
                  <p className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-2">
                    Extras Opcionales
                  </p>
                  <div className="space-y-0 flex-1">
                    <SelectionItem
                      label="1 habitación más"
                      price="+€6.99"
                      checked={basicaExtras.habitacion}
                      onChange={() => setBasicaExtras((p) => ({ ...p, habitacion: !p.habitacion }))}
                    />
                    <SelectionItem
                      label="Tienes mascotas"
                      price="+€1.99"
                      checked={basicaExtras.mascotas}
                      onChange={() => setBasicaExtras((p) => ({ ...p, mascotas: !p.mascotas }))}
                    />
                    <SelectionItem
                      label="Requiere aspiradora"
                      price="+€2.99"
                      checked={basicaExtras.aspiradora}
                      onChange={() =>
                        setBasicaExtras((p) => ({ ...p, aspiradora: !p.aspiradora }))
                      }
                    />
                    <SelectionItem
                      label="Desplazamiento fuera de Barcelona ciudad"
                      price="+€4.99"
                      checked={basicaExtras.desplazamiento}
                      onChange={() =>
                        setBasicaExtras((p) => ({ ...p, desplazamiento: !p.desplazamiento }))
                      }
                    />
                    <SelectionItem
                      label="Requiere productos limpieza"
                      price="+€4.99"
                      checked={basicaExtras.productos}
                      onChange={() => setBasicaExtras((p) => ({ ...p, productos: !p.productos }))}
                    />
                  </div>
                  <a
                    href="#contacto"
                    className="mt-6 block w-full py-3.5 text-center bg-orange-500 text-white rounded-xl font-bold hover:bg-orange-600 transition-all"
                  >
                    Reservar — €{basicaTotal.toFixed(2)}
                  </a>
                </div>
              </div>

              {/* Profunda */}
              <div className="bg-white rounded-2xl overflow-hidden shadow-sm border border-gray-100 flex flex-col">
                <div className="h-52 overflow-hidden relative">
                  <Image
                    src="https://images.unsplash.com/photo-1527515637462-cff94eebd21d?auto=format&fit=crop&q=80&w=800"
                    width={800}
                    height={450}
                    alt="Limpieza Profunda de Casa"
                    className="w-full h-full object-cover"
                    loading="lazy"
                  />
                  <div className="absolute top-3 right-3 bg-[#1e3a5f] text-white px-3 py-1.5 rounded-full text-xs font-bold">
                    Más popular
                  </div>
                </div>
                <div className="p-6 flex flex-col flex-1">
                  <h3 className="text-lg font-bold text-[#1e3a5f] mb-1">
                    Limpieza Profunda de Casa
                  </h3>
                  <p className="text-sm text-gray-500 mb-4">
                    Una limpieza a fondo para dejar tu hogar como nuevo. 3 horas de servicio
                    profesional.
                  </p>
                  <div className="flex items-baseline gap-2 mb-4">
                    <span className="text-3xl font-extrabold text-[#1e3a5f]">
                      €{profundaTotal.toFixed(2)}
                    </span>
                    <span className="text-sm text-gray-400">3 horas</span>
                  </div>
                  <ul className="space-y-1.5 mb-4">
                    {[
                      'Limpieza de hornos',
                      'Limpieza de ventanas',
                      '3 habitaciones',
                      'Sala comedor',
                      '1 baño',
                      'Cocina',
                      'Puertas',
                      'Entrada',
                    ].map((item) => (
                      <li key={item} className="flex items-center gap-2 text-sm text-gray-700">
                        <Check className="w-4 h-4 text-emerald-500 shrink-0" /> {item}
                      </li>
                    ))}
                  </ul>
                  <p className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-2">
                    Extras Opcionales
                  </p>
                  <div className="space-y-0 flex-1">
                    <SelectionItem
                      label="1 baño más"
                      price="+€6.99"
                      checked={profundaExtras.bano}
                      onChange={() => setProfundaExtras((p) => ({ ...p, bano: !p.bano }))}
                    />
                    <SelectionItem
                      label="1 habitación más"
                      price="+€5.99"
                      checked={profundaExtras.habitacion}
                      onChange={() =>
                        setProfundaExtras((p) => ({ ...p, habitacion: !p.habitacion }))
                      }
                    />
                    <SelectionItem
                      label="Lavar platos y organizar (20u)"
                      price="+€4.99"
                      checked={profundaExtras.platos}
                      onChange={() => setProfundaExtras((p) => ({ ...p, platos: !p.platos }))}
                    />
                    <SelectionItem
                      label="Balcón"
                      price="+€5.99"
                      checked={profundaExtras.balcon}
                      onChange={() => setProfundaExtras((p) => ({ ...p, balcon: !p.balcon }))}
                    />
                    <SelectionItem
                      label="Planchar ropa (20u)"
                      price="+€19.99"
                      checked={profundaExtras.planchar}
                      onChange={() => setProfundaExtras((p) => ({ ...p, planchar: !p.planchar }))}
                    />
                    <SelectionItem
                      label="Limpieza de moho"
                      price="+€8.99"
                      checked={profundaExtras.moho}
                      onChange={() => setProfundaExtras((p) => ({ ...p, moho: !p.moho }))}
                    />
                  </div>
                  <a
                    href="#contacto"
                    className="mt-6 block w-full py-3.5 text-center bg-orange-500 text-white rounded-xl font-bold hover:bg-orange-600 transition-all"
                  >
                    Reservar — €{profundaTotal.toFixed(2)}
                  </a>
                </div>
              </div>

              {/* Fin de Obra */}
              <div className="bg-white rounded-2xl overflow-hidden shadow-sm border border-gray-100 flex flex-col">
                <div className="h-52 overflow-hidden relative">
                  <Image
                    src="https://images.unsplash.com/photo-1558618666-fcd25c85f82e?auto=format&fit=crop&q=80&w=800"
                    width={800}
                    height={450}
                    alt="Limpieza Fin de Obra"
                    className="w-full h-full object-cover"
                    loading="lazy"
                  />
                  <div className="absolute top-3 right-3 bg-[#1e3a5f] text-white px-3 py-1.5 rounded-full text-xs font-bold">
                    Profesional
                  </div>
                </div>
                <div className="p-6 flex flex-col flex-1">
                  <h3 className="text-lg font-bold text-[#1e3a5f] mb-1">Limpieza Fin de Obra</h3>
                  <p className="text-sm text-gray-500 mb-4">
                    Todo lo de limpieza profunda más servicios especializados post-obra. 3 horas
                    incluidas.
                  </p>
                  <div className="flex items-baseline gap-2 mb-4">
                    <span className="text-3xl font-extrabold text-[#1e3a5f]">€49.99</span>
                    <span className="text-sm text-gray-400">3 horas</span>
                  </div>
                  <ul className="space-y-1.5 flex-1">
                    {[
                      'Todo lo de Limpieza Profunda',
                      'Limpieza de paredes y polvo',
                      'Despegar pintura del suelo',
                      'Tirar basuras',
                    ].map((item) => (
                      <li key={item} className="flex items-center gap-2 text-sm text-gray-700">
                        <Check className="w-4 h-4 text-emerald-500 shrink-0" /> {item}
                      </li>
                    ))}
                  </ul>
                  <a
                    href="#contacto"
                    className="mt-6 block w-full py-3.5 text-center bg-orange-500 text-white rounded-xl font-bold hover:bg-orange-600 transition-all"
                  >
                    Reservar — €49.99
                  </a>
                </div>
              </div>
            </div>

            {/* Sofás / Alfombras / Colchones */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-6">
              {/* Sofás */}
              <div className="bg-white rounded-2xl overflow-hidden shadow-sm border border-gray-100 flex flex-col">
                <div className="h-52 overflow-hidden">
                  <Image
                    src="https://images.unsplash.com/photo-1555041469-a586c61ea9bc?auto=format&fit=crop&q=80&w=800"
                    width={800}
                    height={450}
                    alt="Limpieza de Sofás"
                    className="w-full h-full object-cover"
                    loading="lazy"
                  />
                </div>
                <div className="p-6 flex flex-col flex-1">
                  <h3 className="text-lg font-bold text-[#1e3a5f] mb-1">Limpieza de Sofás</h3>
                  <p className="text-sm text-gray-500 mb-4">
                    Limpieza profesional de tapicería. Resultados visibles al instante.
                  </p>
                  <div className="space-y-0 flex-1">
                    <SelectionItem
                      label="4 plazas"
                      price="€100.00"
                      checked={sofasSelected.s4plazas}
                      onChange={() =>
                        setSofasSelected((p) => ({ ...p, s4plazas: !p.s4plazas }))
                      }
                    />
                    <SelectionItem
                      label="3 plazas"
                      price="€85.00"
                      checked={sofasSelected.s3plazas}
                      onChange={() =>
                        setSofasSelected((p) => ({ ...p, s3plazas: !p.s3plazas }))
                      }
                    />
                    <SelectionItem
                      label="2 plazas"
                      price="€55.00"
                      checked={sofasSelected.s2plazas}
                      onChange={() =>
                        setSofasSelected((p) => ({ ...p, s2plazas: !p.s2plazas }))
                      }
                    />
                    <SelectionItem
                      label="Sillas comedor (unidad)"
                      price="€8.00"
                      checked={sofasSelected.sillasComedor}
                      onChange={() =>
                        setSofasSelected((p) => ({ ...p, sillasComedor: !p.sillasComedor }))
                      }
                    />
                    <SelectionItem
                      label="Sillas reclinables (unidad)"
                      price="€20.00"
                      checked={sofasSelected.sillasReclinables}
                      onChange={() =>
                        setSofasSelected((p) => ({ ...p, sillasReclinables: !p.sillasReclinables }))
                      }
                    />
                  </div>
                  {sofasTotal > 0 && (
                    <div className="flex items-center justify-between pt-4 mt-4 border-t border-gray-100">
                      <span className="text-sm text-gray-500">Total seleccionado</span>
                      <span className="text-2xl font-extrabold text-[#1e3a5f]">
                        €{sofasTotal.toFixed(2)}
                      </span>
                    </div>
                  )}
                  <a
                    href="#contacto"
                    className="mt-4 block w-full py-3.5 text-center bg-orange-500 text-white rounded-xl font-bold hover:bg-orange-600 transition-all"
                  >
                    {sofasTotal > 0 ? `Reservar — €${sofasTotal.toFixed(2)}` : 'Seleccionar opciones'}
                  </a>
                </div>
              </div>

              {/* Alfombras */}
              <div className="bg-white rounded-2xl overflow-hidden shadow-sm border border-gray-100 flex flex-col">
                <div className="h-52 overflow-hidden">
                  <Image
                    src="https://images.unsplash.com/photo-1583847268964-b28dc8f51f92?auto=format&fit=crop&q=80&w=800"
                    width={800}
                    height={450}
                    alt="Limpieza de Alfombras"
                    className="w-full h-full object-cover"
                    loading="lazy"
                  />
                </div>
                <div className="p-6 flex flex-col flex-1">
                  <h3 className="text-lg font-bold text-[#1e3a5f] mb-1">
                    Limpieza de Alfombras
                  </h3>
                  <p className="text-sm text-gray-500 mb-4">
                    Eliminación profunda de manchas, ácaros y olores de tus alfombras.
                  </p>
                  <div className="space-y-0 flex-1">
                    <SelectionItem
                      label="2 a 4 metros"
                      price="€40.00"
                      checked={alfombraSelected === '2a4'}
                      onChange={() => setAlfombraSelected((p) => (p === '2a4' ? null : '2a4'))}
                    />
                    <SelectionItem
                      label="4 a 7 metros"
                      price="€70.00"
                      checked={alfombraSelected === '4a7'}
                      onChange={() => setAlfombraSelected((p) => (p === '4a7' ? null : '4a7'))}
                    />
                  </div>
                  <a
                    href="#contacto"
                    className="mt-6 block w-full py-3.5 text-center bg-orange-500 text-white rounded-xl font-bold hover:bg-orange-600 transition-all"
                  >
                    {alfombraPrice
                      ? `Reservar — €${alfombraPrice.toFixed(2)}`
                      : 'Seleccionar opciones'}
                  </a>
                </div>
              </div>

              {/* Colchones */}
              <div className="bg-white rounded-2xl overflow-hidden shadow-sm border border-gray-100 flex flex-col">
                <div className="h-52 overflow-hidden relative">
                  <Image
                    src="https://images.unsplash.com/photo-1631049307264-da0ec9d70304?auto=format&fit=crop&q=80&w=800"
                    width={800}
                    height={450}
                    alt="Limpieza de Colchón"
                    className="w-full h-full object-cover"
                    loading="lazy"
                  />
                  <div className="absolute top-3 right-3 bg-orange-500 text-white px-3 py-1.5 rounded-full text-xs font-bold">
                    🔥 Oferta Especial
                  </div>
                </div>
                <div className="p-6 flex flex-col flex-1">
                  <h3 className="text-lg font-bold text-[#1e3a5f] mb-1">Limpieza de Colchón</h3>
                  <p className="text-sm text-gray-500 mb-4">
                    Eliminación de ácaros, manchas y bacterias. Ambas caras incluidas.
                  </p>
                  <div className="space-y-0 flex-1">
                    <SelectionItem
                      label="160×190 (ambas caras)"
                      price="€65.00"
                      originalPrice="€75.00"
                      checked={colchonSelected === '160'}
                      onChange={() => setColchonSelected((p) => (p === '160' ? null : '160'))}
                    />
                    <SelectionItem
                      label="140×190 (ambas caras)"
                      price="€45.00"
                      originalPrice="€55.00"
                      checked={colchonSelected === '140'}
                      onChange={() => setColchonSelected((p) => (p === '140' ? null : '140'))}
                    />
                  </div>
                  <a
                    href="#contacto"
                    className="mt-6 block w-full py-3.5 text-center bg-orange-500 text-white rounded-xl font-bold hover:bg-orange-600 transition-all"
                  >
                    {colchonPrice
                      ? `Reservar — €${colchonPrice.toFixed(2)}`
                      : 'Seleccionar opciones'}
                  </a>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Contact Section */}
        <section id="contacto" className="py-20 bg-white">
          <div className="max-w-6xl mx-auto px-6">
            <div className="grid lg:grid-cols-2 gap-16 items-start">
              <div>
                <h2 className="text-4xl lg:text-5xl font-extrabold text-[#1e3a5f] mb-4 leading-tight">
                  Solicita tu presupuesto gratuito
                </h2>
                <p className="text-gray-500 mb-8 text-lg leading-relaxed">
                  Déjanos tus datos y te enviaremos un presupuesto personalizado en menos de 1 hora.
                  Sin compromiso.
                </p>

                <div className="space-y-4">
                  <div className="flex items-center gap-4 p-5 rounded-2xl bg-gray-50 border border-gray-100">
                    <div className="w-12 h-12 rounded-full bg-gray-100 flex items-center justify-center shrink-0">
                      <Phone className="w-5 h-5 text-gray-600" />
                    </div>
                    <div>
                      <p className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-0.5">
                        Teléfono
                      </p>
                      <a
                        href="tel:+34674571497"
                        className="text-xl font-bold text-[#1e3a5f] hover:text-orange-500 transition-colors"
                      >
                        +34 674 571 497
                      </a>
                    </div>
                  </div>

                  <a
                    href="https://wa.me/34674571497"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-4 p-5 rounded-2xl bg-emerald-50 border border-emerald-100 hover:bg-emerald-100 transition-all"
                  >
                    <div className="w-12 h-12 rounded-full bg-emerald-100 flex items-center justify-center shrink-0">
                      <MessageCircle className="w-5 h-5 text-emerald-600" />
                    </div>
                    <div>
                      <p className="text-xs font-bold text-emerald-600 uppercase tracking-widest mb-0.5">
                        WhatsApp
                      </p>
                      <span className="text-xl font-bold text-[#1e3a5f]">
                        Escríbenos por WhatsApp
                      </span>
                    </div>
                  </a>
                </div>

                <p className="mt-6 text-sm text-gray-400">
                  98.4% de satisfacción en limpiezas de fin de obra · Barcelona
                </p>
              </div>

              <div>
                {formStatus === 'success' ? (
                  <div className="bg-white p-10 rounded-3xl border border-emerald-200 shadow-sm text-center space-y-4">
                    <div className="w-16 h-16 rounded-full bg-emerald-50 flex items-center justify-center mx-auto">
                      <Check className="w-8 h-8 text-emerald-500" />
                    </div>
                    <h3 className="text-2xl font-bold text-[#1e3a5f]">¡Solicitud enviada!</h3>
                    <p className="text-gray-500">
                      Te responderemos con tu cotización en menos de 1 hora.
                    </p>
                    <button
                      onClick={() => setFormStatus('idle')}
                      className="text-sm font-medium text-orange-500 hover:underline"
                    >
                      Enviar otra solicitud
                    </button>
                  </div>
                ) : (
                  <form
                    onSubmit={handleSubmit}
                    className="bg-white p-8 rounded-3xl border border-gray-100 shadow-sm space-y-5"
                  >
                    <input type="hidden" name="_captcha" value="false" />
                    <input
                      type="hidden"
                      name="_subject"
                      value="Nueva solicitud de presupuesto - LimpiaMAX"
                    />
                    <div>
                      <label
                        className="block text-sm font-medium text-gray-600 mb-1.5"
                        htmlFor="name"
                      >
                        Nombre
                      </label>
                      <input
                        className="w-full h-12 rounded-xl border border-gray-200 px-4 text-base focus:outline-none focus:ring-2 focus:ring-orange-400 focus:border-orange-400 transition-colors"
                        id="name"
                        name="name"
                        placeholder="Tu nombre"
                        required
                      />
                    </div>
                    <div>
                      <label
                        className="block text-sm font-medium text-gray-600 mb-1.5"
                        htmlFor="email"
                      >
                        Email
                      </label>
                      <input
                        type="email"
                        className="w-full h-12 rounded-xl border border-gray-200 px-4 text-base focus:outline-none focus:ring-2 focus:ring-orange-400 focus:border-orange-400 transition-colors"
                        id="email"
                        name="email"
                        placeholder="tu@email.com"
                        required
                      />
                    </div>
                    <div>
                      <label
                        className="block text-sm font-medium text-gray-600 mb-1.5"
                        htmlFor="phone"
                      >
                        Teléfono
                      </label>
                      <input
                        type="tel"
                        className="w-full h-12 rounded-xl border border-gray-200 px-4 text-base focus:outline-none focus:ring-2 focus:ring-orange-400 focus:border-orange-400 transition-colors"
                        id="phone"
                        name="phone"
                        placeholder="+34 600 000 000"
                        required
                      />
                    </div>
                    {formStatus === 'error' && (
                      <p className="text-sm text-red-500">
                        Hubo un error. Por favor llámanos directamente.
                      </p>
                    )}
                    <button
                      type="submit"
                      disabled={formStatus === 'sending'}
                      className="w-full py-4 flex items-center justify-center gap-2 bg-orange-500 text-white rounded-xl font-bold text-base shadow-md hover:bg-orange-600 transition-all active:scale-[0.98] disabled:opacity-70 disabled:cursor-not-allowed"
                    >
                      <Send className="w-5 h-5" />
                      {formStatus === 'sending' ? 'Enviando...' : 'Solicitar Reserva'}
                    </button>
                    <p className="text-sm text-center text-gray-400">
                      Te responderemos en menos de 1 hora
                    </p>
                  </form>
                )}
              </div>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-[#1e3a5f] border-t-4 border-orange-500">
        <div className="max-w-7xl mx-auto px-6 py-12">
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
            <div>
              <span className="text-2xl font-bold text-white">
                Limpia<span className="text-orange-500">MAX</span>
              </span>
              <p className="text-white/60 text-sm mt-1">Tu hogar, en su versión MAX.</p>
            </div>
            <div className="flex flex-col sm:flex-row items-start sm:items-center gap-6 text-white/80 text-sm">
              <a
                href="tel:+34674571497"
                className="flex items-center gap-2 hover:text-orange-400 transition-colors"
              >
                <Phone className="w-4 h-4" /> +34 674 571 497
              </a>
              <span className="flex items-center gap-2">
                <MapPin className="w-4 h-4" /> Barcelona, España
              </span>
            </div>
          </div>
          <div className="border-t border-white/10 mt-10 pt-6 text-center text-sm text-white/40">
            © {new Date().getFullYear()} Limpia MAX. Todos los derechos reservados.
          </div>
        </div>
      </footer>
    </div>
  );
}
