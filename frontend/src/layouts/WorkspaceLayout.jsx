import { useState } from 'react';
import { NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom';
import {
  BadgePercent, Bell, Boxes, ChartNoAxesCombined, ChevronDown, CircleDollarSign, ClipboardList, CreditCard,
  Gift, LayoutDashboard, Leaf, LogOut, Menu, Package, RotateCcw, Settings, ShoppingBag, Store, Users, X,
} from 'lucide-react';
import { useDemo } from '../App.jsx';

const adminNav = [
  { label: 'WORKSPACE', items: [{ id: 'overview', label: 'Overview', icon: LayoutDashboard }, { id: 'products', label: 'Products', icon: Package }, { id: 'categories', label: 'Categories', icon: Boxes }, { id: 'wholesalers', label: 'Wholesalers', icon: Users }, { id: 'orders', label: 'Orders', icon: ClipboardList }] },
  { label: 'MANAGE', items: [{ id: 'payments-credit', label: 'Payments & credit', icon: CreditCard }, { id: 'loyalty', label: 'Loyalty settings', icon: BadgePercent }, { id: 'rewards-store', label: 'Rewards Store', icon: Gift }, { id: 'returns', label: 'Returns', icon: RotateCcw }] },
  { label: 'INSIGHTS', items: [{ id: 'reports', label: 'Reports', icon: ChartNoAxesCombined }, { id: 'settings', label: 'Settings', icon: Settings }] },
];
const wholesalerNav = [
  { label: 'YOUR BUSINESS', items: [{ id: 'overview', label: 'Overview', icon: LayoutDashboard }, { id: 'products', label: 'Browse products', icon: Package }, { id: 'cart', label: 'Cart & checkout', icon: ShoppingBag }, { id: 'orders', label: 'My orders', icon: ClipboardList }] },
  { label: 'YOUR REWARDS', items: [{ id: 'payments-credit', label: 'Payments & credit', icon: CreditCard }, { id: 'my-rewards', label: 'My rewards', icon: BadgePercent }, { id: 'rewards-store', label: 'Rewards Store', icon: Gift }, { id: 'returns', label: 'Returns', icon: RotateCcw }] },
  { label: 'ACCOUNT', items: [{ id: 'profile', label: 'Business profile', icon: Store }] },
];

export default function WorkspaceLayout() {
  const { session, signOut, cart } = useDemo();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const role = session?.role || 'admin';
  const nav = role === 'admin' ? adminNav : wholesalerNav;
  const title = role === 'admin' ? 'Factory Admin' : 'Wholesaler';
  const initials = role === 'admin' ? 'RK' : 'AW';

  const linkTo = (id) => `/${role}/${id}`;
  const isCurrent = (id) => location.pathname === linkTo(id) || (id === 'products' && location.pathname.endsWith('/products'));
  const sidebar = <aside className={`sidebar ${mobileOpen ? 'sidebar-open' : ''}`}>
    <div className="sidebar-brand"><NavLink to={linkTo('overview')} className="brand"><span className="brand-mark"><Leaf size={18} /></span>groomix</NavLink><button className="mobile-close icon-button" onClick={() => setMobileOpen(false)} aria-label="Close menu"><X size={19} /></button></div>
    <div className="workspace-select"><span className="workspace-logo">G</span><span><strong>Groomix Wholesale</strong><small>{title} workspace</small></span><ChevronDown size={15} /></div>
    <nav className="side-nav">{nav.map((group) => <div className="nav-group" key={group.label}><span className="nav-label">{group.label}</span>{group.items.map(({ id, label, icon: Icon }) =>
      <NavLink key={id} to={linkTo(id)} onClick={() => setMobileOpen(false)} className={() => `nav-link ${isCurrent(id) ? 'nav-active' : ''}`}>
        <Icon size={17} strokeWidth={1.8} /><span>{label}</span>{id === 'cart' && cart.length > 0 && <b className="nav-count">{cart.length}</b>}
      </NavLink>)}</div>)}</nav>
    <div className="sidebar-bottom"><div className="help-card"><span className="help-dot" /><strong>Need a hand?</strong><p>Our partner team is here to help.</p><button onClick={() => window.alert('Demo support: hello@groomix.example')}>Contact support <span>↗</span></button></div>
      <button className="signout-link" onClick={() => { signOut(); navigate('/login'); }}><LogOut size={16} />Sign out of demo</button></div>
  </aside>;

  return <div className="app-shell">
    {mobileOpen && <button className="mobile-scrim" aria-label="Close navigation" onClick={() => setMobileOpen(false)} />}
    {sidebar}
    <div className="main-shell">
      <header className="topbar"><button className="mobile-menu icon-button" onClick={() => setMobileOpen(true)} aria-label="Open menu"><Menu size={20} /></button>
        <div className="breadcrumb"><span>Groomix</span><b>/</b><strong>{nav.flatMap((group) => group.items).find((item) => isCurrent(item.id))?.label || 'Workspace'}</strong></div>
        <div className="topbar-actions"><span className="demo-badge"><i /> DEMO MODE</span><button className="icon-button notification-button" aria-label="Notifications" onClick={() => window.alert('You’re all caught up in this demo.')}><Bell size={18} /><i /></button>
          <div className="topbar-divider" /><button className="profile-menu" onClick={() => setProfileOpen(!profileOpen)}><span className="profile-avatar">{initials}</span><span className="profile-text"><strong>{session?.name}</strong><small>{title}</small></span><ChevronDown size={14} /></button>
          {profileOpen && <div className="profile-dropdown"><button onClick={() => { navigate(linkTo(role === 'admin' ? 'settings' : 'profile')); setProfileOpen(false); }}>Account settings</button><button onClick={() => { signOut(); navigate('/login'); }}>Sign out</button></div>}
        </div>
      </header>
      <main className="page-content"><Outlet /></main>
      <footer className="app-footer"><span>© 2026 Groomix · Partner workspace</span><span>Frontend demo · Sample data</span></footer>
    </div>
  </div>;
}
