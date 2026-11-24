import { X } from 'lucide-react';

export function Button({ children, variant = 'primary', className = '', ...props }) {
  return <button className={`button button-${variant} ${className}`} {...props}>{children}</button>;
}

export function PageHeader({ eyebrow, title, description, action }) {
  return <div className="page-header"><div><p className="eyebrow">{eyebrow}</p><h1>{title}</h1>{description && <p className="page-description">{description}</p>}</div>{action && <div className="page-header-action">{action}</div>}</div>;
}

export function MetricCard({ label, value, note, icon: Icon, tone = 'sage' }) {
  return <article className="metric-card"><div className={`metric-icon tone-${tone}`}><Icon size={18} /></div><p>{label}</p><strong>{value}</strong><span>{note}</span></article>;
}

export function StatusPill({ value }) {
  const tone = /paid|verified|delivered|active|approved|complete/i.test(value) ? 'positive'
    : /pending|review|inspection|processing|dispatched/i.test(value) ? 'warning'
      : /cancel|reject|overdue|refunded/i.test(value) ? 'negative' : 'neutral';
  return <span className={`status-pill status-${tone}`}><i />{value}</span>;
}

export function Modal({ title, children, onClose, wide = false }) {
  return <div className="modal-backdrop" onMouseDown={(event) => event.target === event.currentTarget && onClose()}>
    <section className={`modal ${wide ? 'modal-wide' : ''}`} role="dialog" aria-modal="true" aria-label={title}>
      <div className="modal-heading"><h2>{title}</h2><button className="icon-button" onClick={onClose} aria-label="Close"><X size={18} /></button></div>
      {children}
    </section>
  </div>;
}

export function DataTable({ columns, rows, empty = 'No records to show.' }) {
  if (!rows.length) return <div className="empty-state">{empty}</div>;
  return <div className="table-scroll"><table><thead><tr>{columns.map((column) => <th key={column.key}>{column.label}</th>)}</tr></thead><tbody>
    {rows.map((row, index) => <tr key={row.id || row.ref || row.name || index}>{columns.map((column) => <td key={column.key}>{column.render ? column.render(row) : row[column.key]}</td>)}</tr>)}
  </tbody></table></div>;
}

export function SearchBox({ value, onChange, placeholder = 'Search...' }) {
  return <label className="search-box"><span>⌕</span><input value={value} onChange={(event) => onChange(event.target.value)} placeholder={placeholder} /></label>;
}

