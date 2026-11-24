import { ArrowRight, ArrowUpRight, BadgeIndianRupee, Boxes, ClipboardList, CreditCard, Gift, Package, Users } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useDemo } from '../App.jsx';
import { MetricCard, PageHeader, StatusPill } from '../components/UI.jsx';
import { monthlySales } from '../data/demoData.js';

const money = (value) => `₹${Number(value).toLocaleString('en-IN')}`;

function SalesChart() {
  const max = Math.max(...monthlySales.map((item) => item.value));
  return <div className="chart-card panel"><div className="panel-heading"><div><p className="eyebrow">PERFORMANCE</p><h2>Sales overview</h2></div><select aria-label="Sales period" defaultValue="6"><option value="6">Last 6 months</option><option value="12">Last 12 months</option></select></div>
    <div className="chart-total"><strong>₹18.42L</strong><span className="trend-up"><ArrowUpRight size={14} /> 12.8%</span><small>vs. previous period</small></div>
    <div className="bar-chart">{monthlySales.map((item, index) => <div className="bar-column" key={item.month}><div className="bar-track"><div className={`bar-fill ${index === monthlySales.length - 1 ? 'bar-current' : ''}`} style={{ height: `${(item.value / max) * 100}%` }} title={`${item.value} sales index`} /></div><span>{item.month}</span></div>)}</div>
    <div className="chart-legend"><span><i /> Wholesale sales</span><small>Sample data · illustrative only</small></div>
  </div>;
}

function RecentActivity({ admin, orders }) {
  const rows = (admin ? orders : orders.filter((order) => order.wholesaler === 'Aarav Wellness Mart')).slice(0, 5);
  return <div className="panel recent-panel"><div className="panel-heading"><div><p className="eyebrow">{admin ? 'LATEST ACTIVITY' : 'YOUR PURCHASES'}</p><h2>{admin ? 'Recent orders' : 'Recent orders'}</h2></div><Link className="text-link" to={`/${admin ? 'admin' : 'wholesaler'}/orders`}>View all <ArrowRight size={14} /></Link></div>
    <div className="recent-list">{rows.map((order) => <div className="recent-row" key={order.id}><div className="order-icon"><Package size={17} /></div><div className="recent-info"><strong>{order.id}</strong><span>{admin ? order.wholesaler : `${order.items} product groups`} · {order.date}</span></div><div className="recent-end"><strong>{money(order.amount)}</strong><StatusPill value={order.status} /></div></div>)}</div>
  </div>;
}

export default function DashboardPage() {
  const { session, orders } = useDemo();
  const admin = session?.role === 'admin';
  return <div className="page-wrap">
    <PageHeader eyebrow={`${admin ? 'FACTORY ADMIN' : 'WHOLESALER'} WORKSPACE · MONDAY, 24 NOVEMBER`} title={admin ? 'Good morning, Rhea' : 'Good morning, Aarav'} description={admin ? 'Here’s what’s happening across your wholesale business today.' : 'Your business at a glance. Here’s what’s new in your Groomix workspace.'}
      action={admin ? null : <Link className="button button-primary" to="/wholesaler/products"><Package size={16} /> Browse products</Link>} />
    <div className="metric-grid">
      {admin ? <>
        <MetricCard label="Total wholesalers" value="248" note={<><span className="trend-up"><ArrowUpRight size={13} /> 8.2%</span> this month</>} icon={Users} />
        <MetricCard label="Total orders" value="1,284" note={<><span className="trend-up"><ArrowUpRight size={13} /> 14.6%</span> vs last month</>} icon={ClipboardList} tone="blue" />
        <MetricCard label="Total sales" value="₹18.42L" note={<><span className="trend-up"><ArrowUpRight size={13} /> 12.8%</span> vs last month</>} icon={BadgeIndianRupee} tone="peach" />
        <MetricCard label="Pending orders" value="12" note={<Link to="/admin/orders" className="metric-link">Needs your attention →</Link>} icon={Boxes} tone="sand" />
        <MetricCard label="Outstanding credit" value="₹6.84L" note="Across 34 active accounts" icon={CreditCard} tone="blue" />
        <MetricCard label="Points issued" value="2.46L" note={<><span className="trend-up"><ArrowUpRight size={13} /> 6.1%</span> this month</>} icon={Gift} />
      </> : <>
        <MetricCard label="Available points" value="8,450" note={<Link to="/wholesaler/my-rewards" className="metric-link">Explore your rewards →</Link>} icon={Gift} />
        <MetricCard label="Pending points" value="1,200" note="Unlock after payment & delivery" icon={BadgeIndianRupee} tone="blue" />
        <MetricCard label="Total orders" value="18" note="Since joining Groomix" icon={ClipboardList} tone="peach" />
        <MetricCard label="Outstanding credit" value="₹24,000" note="Due 12 Dec 2026" icon={CreditCard} tone="sand" />
      </>}
    </div>
    <div className="dashboard-lower"><SalesChart /><div className="dashboard-side"><RecentActivity admin={admin} orders={orders} />
      <div className="loyalty-callout"><span className="callout-icon"><Gift size={19} /></span><div><p className="eyebrow">A LITTLE EXTRA</p><h3>{admin ? 'Your rewards are growing' : 'Make every order count'}</h3><p>{admin ? '2,460 points have been earned this month.' : 'Earn points on eligible orders after delivery and full payment.'}</p><Link to={`/${admin ? 'admin' : 'wholesaler'}/${admin ? 'loyalty' : 'my-rewards'}`}>See rewards <ArrowRight size={14} /></Link></div></div>
      </div></div>
  </div>;
}
