// Small shared primitives: Wordmark, Tile, Pill.

export function Wordmark({ accent }) {
  return (
    <div className="flex items-center gap-2.5 select-none">
      <div className="grid place-items-center w-9 h-9 rounded-xl font-black text-ink-950"
           style={{ background: accent, boxShadow: `0 0 18px ${accent}55` }}>W</div>
      <div className="leading-tight">
        <div className="font-semibold tracking-tight text-[15px]">Wise Old Man</div>
        <div className="text-[10px] uppercase tracking-[0.18em] text-mut">command center</div>
      </div>
    </div>
  )
}

export function Tile({ title, action, children, className = '' }) {
  return (
    <section className={`bg-ink-900 border border-line rounded-2xl shadow-tile p-4 flex flex-col min-h-0 ${className}`}>
      <header className="flex items-center justify-between mb-3">
        <h3 className="text-[11px] font-semibold uppercase tracking-[0.14em] text-mut">{title}</h3>
        {action}
      </header>
      <div className="flex-1 min-h-0">{children}</div>
    </section>
  )
}

export function Pill({ children, color, soft = true }) {
  return (
    <span className="text-[10px] px-1.5 py-0.5 rounded-md font-medium tnum"
      style={{ color, background: soft ? color + '1f' : 'transparent', border: `1px solid ${color}40` }}>
      {children}
    </span>
  )
}
