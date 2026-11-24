import { useState } from 'react';
import {
  ArrowDownToLine, ArrowRight, Banknote, Box, Check, ChevronRight, CircleDollarSign,
  ClipboardList, CreditCard, Download, Gift, MapPin, Package, Plus, Send, Settings2,
  ShieldCheck, ShoppingBag, Sparkles, Truck, WalletCards, X,
} from 'lucide-react';
import { Link, useParams } from 'react-router-dom';
import { useDemo } from '../App.jsx';
import { Button, DataTable, Modal, PageHeader, SearchBox, StatusPill } from '../components/UI.jsx';
import { categories, payments, returns, rewardItems, wholesalers } from '../data/demoData.js';

const money = (value) => `₹${Number(value).toLocaleString('en-IN')}`;
const fmt = (value) => new Intl.NumberFormat('en-IN').format(value);

function SectionFrame({ eyebrow, title, description, action, children }) {
  return <div className="page-wrap"><PageHeader eyebrow={eyebrow} title={title} description={description} action={action} />{children}</div>;
}
function Toolbar({ children }) { return <div className="table-toolbar">{children}</div>; }
function Panel({ title, eyebrow, action, children, className = '' }) {
  return <section className={`panel section-panel ${className}`}><div className="panel-heading"><div>{eyebrow && <p className="eyebrow">{eyebrow}</p>}<h2>{title}</h2></div>{action}</div>{children}</section>;
}

function CategoriesPage() {
  const { products, notify } = useDemo();
  const icons = ['✳', '◉', '◌', '✦'];
  return <SectionFrame eyebrow="PRODUCT ORGANIZATION" title="Categories" description="Keep your product collection organized for your wholesale partners.">
    <div className="category-admin-grid">{categories.slice(1).map((category, index) => {
      const count = products.filter((product) => product.category === category).length;
      return <article className="category-admin-card" key={category}><div className={`category-symbol tone-${['sage', 'blue', 'peach', 'sand'][index]}`}>{icons[index]}</div><span className="category-count">{String(count).padStart(2, '0')} PRODUCTS</span><h2>{category}</h2><p>{category === 'Face Care' ? 'Everyday essentials for a fresh, healthy-looking complexion.' : category === 'Hair Care' ? 'Thoughtful routines for stronger, softer, healthier hair.' : category === 'Beard & Grooming' ? 'Easy grooming staples made for everyday confidence.' : 'Feel-good body care made for the whole day.'}</p><button className="text-link" onClick={() => notify(`${category} category opened`)}>View products <ArrowRight size={14} /></button></article>;
    })}</div>
  </SectionFrame>;
}

function WholesalersPage() {
  const [query, setQuery] = useState('');
  const [selected, setSelected] = useState(null);
  const { notify } = useDemo();
  const records = wholesalers.filter((item) => `${item.name} ${item.city}`.toLowerCase().includes(query.toLowerCase()));
  const columns = [
    { key: 'name', label: 'WHOLESALER', render: (row) => <div className="customer-cell"><span className="customer-avatar">{row.initials}</span><span><strong>{row.name}</strong><small>{row.city}</small></span></div> },
    { key: 'orders', label: 'ORDERS' },
    { key: 'sales', label: 'LIFETIME SALES', render: (row) => money(row.sales) },
    { key: 'credit', label: 'CREDIT FACILITY' },
    { key: 'status', label: 'STATUS', render: (row) => <StatusPill value={row.status} /> },
    { key: 'action', label: '', render: (row) => <button className="table-action" onClick={() => setSelected(row)}>Details <ChevronRight size={14} /></button> },
  ];
  return <SectionFrame eyebrow="PARTNER NETWORK" title="Wholesalers" description="Manage your wholesale partners and keep an eye on account health." action={<Button onClick={() => alert('Wholesaler invitations are a demo-only action.')}><Plus size={16} /> Invite wholesaler</Button>}>
    <div className="metric-grid compact-grid"><article className="mini-stat"><span>Active partners</span><strong>248</strong><small>+8 this month</small></article><article className="mini-stat"><span>Awaiting review</span><strong>06</strong><small>Applications to review</small></article><article className="mini-stat"><span>Credit accounts</span><strong>34</strong><small>Across active partners</small></article></div>
    <Panel title="All wholesalers" eyebrow="PARTNER DIRECTORY"><Toolbar><SearchBox value={query} onChange={setQuery} placeholder="Search business or city..." /><button className="button button-secondary button-small" onClick={() => notify('Wholesaler list exported in demo')}><Download size={14} /> Export</button></Toolbar><DataTable columns={columns} rows={records} /></Panel>
    {selected && <Modal title="Wholesaler details" onClose={() => setSelected(null)}><div className="detail-profile"><span className="customer-avatar avatar-large">{selected.initials}</span><div><h3>{selected.name}</h3><span>{selected.city}</span></div></div><div className="detail-grid"><div><small>Total orders</small><strong>{selected.orders}</strong></div><div><small>Lifetime sales</small><strong>{money(selected.sales)}</strong></div><div className="detail-wide"><small>Credit facility</small><strong>{selected.credit}</strong></div></div><div className="modal-actions"><Button variant="secondary" onClick={() => setSelected(null)}>Close</Button><Button onClick={() => alert('Demo: wholesaler record opened')}>View account</Button></div></Modal>}
  </SectionFrame>;
}

function OrdersPage() {
  const { session, orders, updateOrderStatus, notify } = useDemo();
  const admin = session.role === 'admin';
  const [query, setQuery] = useState('');
  const [status, setStatus] = useState('All statuses');
  const [selected, setSelected] = useState(null);
  const ownOrders = admin ? orders : orders.filter((item) => item.wholesaler === 'Aarav Wellness Mart');
  const filtered = ownOrders.filter((item) => (status === 'All statuses' || item.status === status) && `${item.id} ${item.wholesaler} ${item.status}`.toLowerCase().includes(query.toLowerCase()));
  const changeStatus = (order, next) => {
    updateOrderStatus(order.id, next);
    setSelected(null);
    notify(`Order ${order.id} updated to ${next}`);
  };
  const columns = [
    { key: 'id', label: 'ORDER', render: (row) => <button className="cell-link" onClick={() => setSelected(row)}>{row.id}</button> },
    ...(admin ? [{ key: 'wholesaler', label: 'WHOLESALER' }] : []),
    { key: 'date', label: 'DATE' }, { key: 'items', label: 'ITEMS', render: (row) => `${row.items} product groups` },
    { key: 'payment', label: 'PAYMENT', render: (row) => <StatusPill value={row.payment} /> },
    { key: 'amount', label: 'TOTAL', render: (row) => <strong>{money(row.amount)}</strong> },
    { key: 'status', label: 'ORDER STATUS', render: (row) => <StatusPill value={row.status} /> },
    { key: 'action', label: '', render: (row) => <button className="table-action" onClick={() => setSelected(row)}>{admin ? 'Manage' : 'Details'} <ChevronRight size={14} /></button> },
  ];
  const statuses = ['All statuses', 'Pending approval', 'Approved', 'Processing', 'Dispatched', 'Delivered', 'Cancelled'];
  return <SectionFrame eyebrow={admin ? 'ORDER MANAGEMENT' : 'YOUR PURCHASE HISTORY'} title={admin ? 'Orders' : 'My orders'} description={admin ? 'Review incoming orders and follow every shipment through delivery.' : 'See your orders, payment progress and delivery updates.'} action={!admin && <Link className="button button-primary" to="/wholesaler/products"><Plus size={16} /> New order</Link>}>
    <div className="order-status-cards"><div><span>Awaiting approval</span><strong>{orders.filter((item) => item.status === 'Pending approval').length.toString().padStart(2, '0')}</strong></div><div><span>In progress</span><strong>{orders.filter((item) => ['Processing', 'Dispatched'].includes(item.status)).length.toString().padStart(2, '0')}</strong></div><div><span>Delivered this month</span><strong>24</strong></div><div><span>Total order value</span><strong>{money(orders.reduce((sum, item) => sum + item.amount, 0))}</strong></div></div>
    <Panel title={admin ? 'All orders' : 'Order history'} eyebrow="ORDER REGISTER"><Toolbar><SearchBox value={query} onChange={setQuery} placeholder="Search by order number..." /><select className="select-control" value={status} onChange={(e) => setStatus(e.target.value)}>{statuses.map((item) => <option key={item}>{item}</option>)}</select></Toolbar><DataTable columns={columns} rows={filtered} /></Panel>
    {selected && <Modal title={`Order ${selected.id}`} onClose={() => setSelected(null)}><div className="order-detail-top"><StatusPill value={selected.status} /><strong>{money(selected.amount)}</strong></div><div className="timeline"><div className="timeline-step done"><span><Check size={13} /></span><div><strong>Order placed</strong><small>{selected.date}</small></div></div><div className={`timeline-step ${['Processing', 'Dispatched', 'Delivered'].includes(selected.status) ? 'done' : ''}`}><span>2</span><div><strong>Approved & processing</strong><small>Order is prepared by Groomix</small></div></div><div className={`timeline-step ${['Dispatched', 'Delivered'].includes(selected.status) ? 'done' : ''}`}><span>3</span><div><strong>Dispatched</strong><small>On its way to your business</small></div></div><div className={`timeline-step ${selected.status === 'Delivered' ? 'done' : ''}`}><span>4</span><div><strong>Delivered</strong><small>Delivery confirmation</small></div></div></div>
      <div className="order-detail-meta"><span>Wholesaler<strong>{selected.wholesaler}</strong></span><span>Payment method<strong>{selected.payment}</strong></span><span>Product groups<strong>{selected.items}</strong></span></div>
      {admin ? <div className="modal-actions modal-actions-wrap">
        {selected.status === 'Pending approval' && <><Button onClick={() => changeStatus(selected, 'Approved')}><Check size={15} /> Approve order</Button><Button variant="danger" onClick={() => changeStatus(selected, 'Cancelled')}><X size={15} /> Reject</Button></>}
          {selected.status === 'Approved' && <Button onClick={() => changeStatus(selected, 'Processing')}><Package size={15} /> Start processing</Button>}
        {selected.status === 'Processing' && <Button onClick={() => changeStatus(selected, 'Dispatched')}><Truck size={15} /> Mark dispatched</Button>}
        {selected.status === 'Dispatched' && <Button onClick={() => changeStatus(selected, 'Delivered')}><Check size={15} /> Confirm delivery</Button>}
        <Button variant="secondary" onClick={() => setSelected(null)}>Close</Button></div>
        : <div className="modal-actions">{['Pending approval', 'Processing'].includes(selected.status) && <Button variant="danger" onClick={() => changeStatus(selected, 'Cancelled')}>Request cancellation</Button>}<Button variant="secondary" onClick={() => setSelected(null)}>Close</Button></div>}
    </Modal>}
  </SectionFrame>;
}

function CreditPaymentPage() {
  const { session, notify } = useDemo();
  const admin = session.role === 'admin';
  const [query, setQuery] = useState('');
  const [paymentRows, setPaymentRows] = useState(payments);
  const [creditModal, setCreditModal] = useState(false);
  const [creditRequests, setCreditRequests] = useState([
    { id: 'CR-108', name: 'Glow & Go Retail', amount: '₹1,00,000', date: '23 Nov 2026', status: 'Pending review' },
    { id: 'CR-107', name: 'Urban Grooming Co.', amount: '₹3,00,000', date: '20 Nov 2026', status: 'Pending review' },
  ]);
  const paymentColumns = [
    { key: 'ref', label: 'PAYMENT REF' }, ...(admin ? [{ key: 'customer', label: 'WHOLESALER' }, { key: 'order', label: 'ORDER' }] : [{ key: 'order', label: 'ORDER' }]),
    { key: 'date', label: 'DATE' }, { key: 'method', label: 'METHOD' }, { key: 'amount', label: 'AMOUNT', render: (row) => money(row.amount) },
    { key: 'status', label: 'STATUS', render: (row) => <StatusPill value={row.status} /> },
    ...(admin ? [{ key: 'action', label: '', render: (row) => row.status === 'Pending verification' ? <button className="table-action" onClick={() => verifyPayment(row)}>Verify <Check size={14} /></button> : null }] : []),
  ];
  const filteredPayments = paymentRows.filter((item) => (admin || item.customer === 'Aarav Wellness Mart') && `${item.ref} ${item.order} ${item.customer}`.toLowerCase().includes(query.toLowerCase()));
  const verifyPayment = (payment) => {
    setPaymentRows((items) => items.map((item) => item.ref === payment.ref ? { ...item, status: 'Verified' } : item));
    notify(`${payment.ref} marked verified in demo`);
  };
  const decide = (request, status) => {
    setCreditRequests((items) => items.map((item) => item.id === request.id ? { ...item, status } : item));
    notify(`${request.id} ${status.toLowerCase()} in demo`);
  };
  return <SectionFrame eyebrow={admin ? 'FINANCIAL OPERATIONS' : 'YOUR ACCOUNT'} title={admin ? 'Payments & credit' : 'Payments & credit'} description={admin ? 'Review payments, verify proof and manage credit requests.' : 'A clear view of your payments, available credit and due balance.'} action={!admin && <Button onClick={() => setCreditModal(true)}><Plus size={16} /> Request credit</Button>}>
    <div className="finance-summary"><div className="finance-card"><span className="finance-icon"><WalletCards size={18} /></span><small>{admin ? 'Verified sales' : 'Outstanding balance'}</small><strong>{admin ? '₹12,48,600' : '₹24,000'}</strong><span>{admin ? 'This month' : 'Due 12 Dec 2026'}</span></div><div className="finance-card"><span className="finance-icon finance-blue"><CreditCard size={18} /></span><small>{admin ? 'Outstanding credit' : 'Credit limit available'}</small><strong>{admin ? '₹6,84,000' : '₹1,76,000'}</strong><span>{admin ? '34 accounts' : 'of ₹2,00,000 facility'}</span></div><div className="finance-card"><span className="finance-icon finance-peach"><CircleDollarSign size={18} /></span><small>{admin ? 'Awaiting verification' : 'Payments this year'}</small><strong>{admin ? '08 payments' : '₹3,86,400'}</strong><span>{admin ? '₹2,14,800 total' : '18 orders placed'}</span></div></div>
    {admin && <Panel title="Credit requests" eyebrow="DECISIONS NEEDED"><DataTable columns={[
      { key: 'id', label: 'REQUEST' }, { key: 'name', label: 'WHOLESALER' }, { key: 'date', label: 'SUBMITTED' }, { key: 'amount', label: 'REQUESTED LIMIT' },
      { key: 'status', label: 'STATUS', render: (row) => <StatusPill value={row.status} /> },
      { key: 'action', label: '', render: (row) => row.status === 'Pending review' ? <div className="table-actions"><button className="table-action" onClick={() => decide(row, 'Approved')}>Approve</button><button className="table-action danger-link" onClick={() => decide(row, 'Rejected')}>Reject</button></div> : null },
    ]} rows={creditRequests} /></Panel>}
    <Panel title={admin ? 'Payment history' : 'Your payment history'} eyebrow="PAYMENTS"><Toolbar><SearchBox value={query} onChange={setQuery} placeholder="Search payment or order..." /><button className="button button-secondary button-small" onClick={() => notify('Payment history download prepared in demo')}><ArrowDownToLine size={14} /> Download</button></Toolbar><DataTable columns={paymentColumns} rows={filteredPayments} /></Panel>
    {!admin && <Panel title="Credit facility" eyebrow="YOUR APPROVED TERMS"><div className="credit-overview"><div><small>Available credit</small><strong>₹1,76,000</strong></div><div className="credit-meter"><span style={{ width: '12%' }} /></div><div className="credit-foot"><span>₹24,000 used</span><span>₹2,00,000 limit</span></div><p>Payment terms: 30 days · Facility valid through 31 Mar 2027</p></div></Panel>}
    {creditModal && <Modal title="Request a credit facility" onClose={() => setCreditModal(false)}><p className="form-note">Credit requests are for demonstration only. An admin would review eligibility before approving a facility.</p><form className="form-stack" onSubmit={(e) => { e.preventDefault(); setCreditModal(false); notify('Credit request submitted in demo'); }}><label>Requested limit<select defaultValue="₹1,00,000"><option>₹50,000</option><option>₹1,00,000</option><option>₹2,00,000</option><option>₹3,00,000</option></select></label><label>Reason for request<textarea rows="3" required placeholder="Tell us briefly about your business needs" /></label><label className="checkbox-line"><input type="checkbox" required /> I understand this request is subject to eligibility review.</label><div className="modal-actions"><Button type="button" variant="secondary" onClick={() => setCreditModal(false)}>Cancel</Button><Button type="submit"><Send size={15} /> Submit request</Button></div></form></Modal>}
  </SectionFrame>;
}

function LoyaltyPage() {
  const { notify, products } = useDemo();
  const [budget, setBudget] = useState(10);
  const [conversion, setConversion] = useState(100);
  const [minimum, setMinimum] = useState(1000);
  const [discount, setDiscount] = useState(20);
  const [expiry, setExpiry] = useState(12);
  const [rates, setRates] = useState({});
  return <SectionFrame eyebrow="LOYALTY PROGRAM" title="Loyalty settings" description="Set thoughtful reward rules that protect margin and make every purchase count." action={<Button onClick={() => notify('Loyalty settings saved in demo')}><Check size={16} /> Save changes</Button>}>
    <div className="settings-layout"><div className="settings-main">
      <Panel title="Earning & redemption" eyebrow="PROGRAM RULES"><p className="section-lead">These settings are sample values and can be changed to suit your business.</p><div className="form-grid settings-fields">
        <label>Reward budget (% of gross profit)<span className="suffix-input"><input type="number" min="0" max="100" value={budget} onChange={(e) => setBudget(e.target.value)} /><i>%</i></span><small>Share of product gross profit allocated to loyalty.</small></label>
        <label>Points conversion rate<span className="suffix-input"><input type="number" min="1" value={conversion} onChange={(e) => setConversion(e.target.value)} /><i>pts = ₹1</i></span><small>Points required to redeem ₹1 at checkout.</small></label>
        <label>Minimum redemption points<span className="suffix-input"><input type="number" min="0" value={minimum} onChange={(e) => setMinimum(e.target.value)} /><i>pts</i></span><small>Smallest points balance usable for redemption.</small></label>
        <label>Maximum checkout discount<span className="suffix-input"><input type="number" min="0" max="100" value={discount} onChange={(e) => setDiscount(e.target.value)} /><i>%</i></span><small>Maximum share of an eligible order payable with points.</small></label>
        <label>Points expiry period<span className="suffix-input"><input type="number" min="1" value={expiry} onChange={(e) => setExpiry(e.target.value)} /><i>months</i></span><small>Points expire this many months after they are earned.</small></label>
      </div></Panel>
      <Panel title="Product-wise earning rates" eyebrow="MARGIN-AWARE REWARDS"><p className="section-lead">Set a per-box points rate. Keep it within your reward budget for each product.</p><div className="rate-list">{products.slice(0, 7).map((product) => <div className="rate-row" key={product.id}><span className={`rate-product-icon art-${product.color}`}>{product.emoji}</span><span className="rate-product"><strong>{product.name}</strong><small>{product.category} · {money(product.price)} per box</small></span><label className="rate-input"><input aria-label={`${product.name} points per box`} type="number" min="0" value={rates[product.id] ?? Math.floor((product.price - product.cost) * (Number(budget) / 100) * (Number(conversion) / 100))} onChange={(e) => setRates({ ...rates, [product.id]: e.target.value })} /><span>pts / box</span></label></div>)}</div></Panel>
    </div><aside className="settings-aside"><div className="loyalty-preview"><span className="preview-icon"><Sparkles size={18} /></span><p className="eyebrow">HOW IT ADDS UP</p><h3>Rewards that respect your margin.</h3><p>At the current settings, sample points are calculated using the product's gross profit and your reward budget.</p><div className="preview-example"><span>Example · Daily Reset Face Wash</span><div><small>Gross profit per box</small><strong>{money(480 - 312)}</strong></div><div><small>Illustrative reward value</small><strong>{money((480 - 312) * Number(budget) / 100)}</strong></div><div><small>Approx. points earned</small><strong>{fmt(Math.floor((480 - 312) * Number(budget) / 100 * Number(conversion) / 100))} pts</strong></div></div><small className="preview-disclaimer">Illustration only. Points are credited after delivery and full payment.</small></div><div className="aside-note"><ShieldCheck size={18} /><p><strong>Keep rewards sustainable</strong><br />Review product costs and reward rates together when costs change.</p></div></aside></div>
  </SectionFrame>;
}

function RewardsStorePage() {
  const { session, notify, pointsBalance, setPointsBalance } = useDemo();
  const admin = session.role === 'admin';
  const [items, setItems] = useState(rewardItems);
  const [redemptions, setRedemptions] = useState([
    { id: 'RD-0342', customer: 'Aarav Wellness Mart', item: 'Signature Travel Pouch', points: 6500, date: '23 Nov 2026', status: 'Pending approval' },
    { id: 'RD-0341', customer: 'The Good Shelf', item: 'Everyday Essentials Kit', points: 12000, date: '22 Nov 2026', status: 'Dispatched' },
  ]);
  const [editing, setEditing] = useState(null);
  const [selectedReward, setSelectedReward] = useState(null);
  const handleSave = (event) => {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    const updated = { ...editing, name: data.get('name'), type: data.get('type'), points: Number(data.get('points')), stock: Number(data.get('stock')) };
    setItems((current) => current.some((item) => item.id === editing.id) ? current.map((item) => item.id === editing.id ? updated : item) : [...current, { ...updated, id: Date.now() }]);
    setEditing(null); notify('Reward item saved in demo');
  };
  const redeemReward = (item) => {
    setPointsBalance((balance) => balance - item.points);
    setItems((current) => current.map((reward) => reward.id === item.id ? { ...reward, stock: reward.stock - 1 } : reward));
    setRedemptions((current) => [{
      id: `RD-${String(343 + current.length).padStart(4, '0')}`,
      customer: 'Aarav Wellness Mart',
      item: item.name,
      points: item.points,
      date: '24 Nov 2026',
      status: 'Pending approval',
    }, ...current]);
    notify(`Redemption requested for ${item.name}`);
  };
  const updateRedemption = (row, status) => { setRedemptions((list) => list.map((item) => item.id === row.id ? { ...item, status } : item)); notify(`${row.id} ${status.toLowerCase()}`); };
  const columns = [
    { key: 'id', label: 'REDEMPTION' }, { key: 'customer', label: 'WHOLESALER' }, { key: 'item', label: 'REWARD ITEM' }, { key: 'points', label: 'POINTS', render: (row) => `${fmt(row.points)} pts` }, { key: 'date', label: 'DATE' }, { key: 'status', label: 'STATUS', render: (row) => <StatusPill value={row.status} /> },
    { key: 'actions', label: '', render: (row) => row.status === 'Pending approval' ? <div className="table-actions"><button className="table-action" onClick={() => updateRedemption(row, 'Approved')}>Approve</button><button className="table-action danger-link" onClick={() => updateRedemption(row, 'Rejected')}>Reject</button></div> : row.status === 'Approved' ? <button className="table-action" onClick={() => updateRedemption(row, 'Dispatched')}>Dispatch <Truck size={14} /></button> : row.status === 'Dispatched' ? <button className="table-action" onClick={() => updateRedemption(row, 'Delivered')}>Delivered <Check size={14} /></button> : null },
  ];
  return <SectionFrame eyebrow="POINTS, MEET PERKS" title="Rewards Store" description={admin ? 'Manage reward items, stock and partner redemption requests.' : 'A few good things, earned with every eligible order.'} action={admin && <Button onClick={() => setEditing({ name: '', type: 'Groomix product', points: 0, stock: 0, emoji: '🎁', color: 'sage' })}><Plus size={16} /> Add reward item</Button>}>
    {!admin && <div className="points-banner"><span className="points-banner-icon"><Gift size={22} /></span><div><small>YOUR AVAILABLE BALANCE</small><strong>{fmt(pointsBalance)} <i>points</i></strong></div><span className="points-banner-note">Earned on eligible orders after delivery & full payment</span></div>}
    {admin ? <><div className="reward-admin-grid">{items.map((item) => <article className="reward-admin-card" key={item.id}><div className={`reward-art art-${item.color}`}><span>{item.emoji}</span><small>GROOMIX REWARDS</small></div><div className="reward-card-body"><span className="product-category">{item.type}</span><h3>{item.name}</h3><div className="reward-meta"><strong>{fmt(item.points)} pts</strong><span>{item.stock} in stock</span></div><Button variant="secondary" className="full-button" onClick={() => setEditing(item)}>Edit item</Button></div></article>)}</div><Panel title="Redemption requests" eyebrow="FULFILLMENT QUEUE"><DataTable columns={columns} rows={redemptions} /></Panel></>
      : <><div className="reward-store-grid">{items.map((item) => <article className="reward-store-card" key={item.id}><div className={`reward-art art-${item.color}`}><span>{item.emoji}</span><small>GROOMIX REWARDS</small></div><div className="reward-card-body"><span className="product-category">{item.type}</span><h3>{item.name}</h3><div className="reward-meta"><strong><Gift size={15} /> {fmt(item.points)} pts</strong><span>{item.stock > 10 ? 'In stock' : `Only ${item.stock} left`}</span></div><Button className="full-button" disabled={item.stock < 1 || pointsBalance < item.points} onClick={() => setSelectedReward(item)}>{pointsBalance < item.points ? 'Not enough points' : 'Redeem points'} <ArrowRight size={15} /></Button></div></article>)}</div>
        <Panel title="Your redemptions" eyebrow="REDEMPTION HISTORY"><DataTable columns={[{ key: 'id', label: 'REFERENCE' }, { key: 'item', label: 'REWARD' }, { key: 'points', label: 'POINTS USED', render: (row) => `${fmt(row.points)} pts` }, { key: 'date', label: 'REQUESTED' }, { key: 'status', label: 'STATUS', render: (row) => <StatusPill value={row.status} /> }]} rows={redemptions.filter((row) => row.customer === 'Aarav Wellness Mart')} /></Panel></>}
    {editing && <Modal title={editing.id ? 'Edit reward item' : 'Add reward item'} onClose={() => setEditing(null)}><p className="form-note">Reward stock is separate from regular product inventory.</p><form className="form-stack" onSubmit={handleSave}><label>Reward name<input name="name" required defaultValue={editing.name} placeholder="e.g. Groomix travel kit" /></label><label>Item type<select name="type" defaultValue={editing.type}>{['Groomix product', 'Grooming kit', 'Merchandise', 'Gift item'].map((type) => <option key={type}>{type}</option>)}</select></label><label>Points required<input name="points" type="number" min="1" required defaultValue={editing.points} /></label><label>Available reward stock<input name="stock" type="number" min="0" required defaultValue={editing.stock} /></label><div className="modal-actions"><Button type="button" variant="secondary" onClick={() => setEditing(null)}>Cancel</Button><Button type="submit">Save reward</Button></div></form></Modal>}
    {selectedReward && <Modal title="Confirm reward redemption" onClose={() => setSelectedReward(null)}><div className="confirmation-symbol"><Gift size={22} /></div><h3 className="confirm-title">{selectedReward.name}</h3><p className="form-note">This demo request uses <strong>{fmt(selectedReward.points)} points</strong>. Your balance will change from <strong>{fmt(pointsBalance)} to {fmt(pointsBalance - selectedReward.points)} points</strong>, and one item will be reserved.</p><div className="modal-actions"><Button variant="secondary" onClick={() => setSelectedReward(null)}>Keep browsing</Button><Button onClick={() => { redeemReward(selectedReward); setSelectedReward(null); }}>Confirm redemption</Button></div></Modal>}
  </SectionFrame>;
}

function ReturnsPage() {
  const { session, notify } = useDemo();
  const admin = session.role === 'admin';
  const [rows, setRows] = useState(returns);
  const [modal, setModal] = useState(false);
  const [query, setQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('All statuses');
  const visible = rows.filter((row) => (admin || row.customer === 'Aarav Wellness Mart')
    && (statusFilter === 'All statuses' || row.status === statusFilter)
    && `${row.id} ${row.order} ${row.customer} ${row.item}`.toLowerCase().includes(query.toLowerCase()));
  const change = (row, status) => { setRows((current) => current.map((item) => item.id === row.id ? { ...item, status } : item)); notify(`${row.id}: ${status.toLowerCase()}`); };
  const columns = [
    { key: 'id', label: 'RETURN' }, ...(admin ? [{ key: 'customer', label: 'WHOLESALER' }] : []), { key: 'order', label: 'ORDER' }, { key: 'date', label: 'REQUESTED' }, { key: 'item', label: 'ITEM & QUANTITY' }, { key: 'reason', label: 'REASON' }, { key: 'status', label: 'STATUS', render: (row) => <StatusPill value={row.status} /> },
    { key: 'action', label: '', render: (row) => admin && !['Rejected', 'Approved'].includes(row.status) ? <div className="table-actions">{row.status === 'Needs inspection' ? <button className="table-action" onClick={() => change(row, 'Inspected')}>Mark inspected</button> : <button className="table-action" onClick={() => change(row, 'Approved')}>Approve return</button>}<button className="table-action danger-link" onClick={() => change(row, 'Rejected')}>Reject</button></div> : null },
  ];
  return <SectionFrame eyebrow={admin ? 'RETURNS & QUALITY' : 'AFTER-SALES SUPPORT'} title={admin ? 'Returns' : 'Returns & issues'} description={admin ? 'Review return requests and record inspection outcomes.' : 'Need help with an order? Raise a request and track what happens next.'} action={!admin && <Button onClick={() => setModal(true)}><Plus size={16} /> Raise a return request</Button>}>
    <Panel title={admin ? 'Return requests' : 'Your return requests'} eyebrow="REQUEST REGISTER"><Toolbar><SearchBox value={query} onChange={setQuery} placeholder="Search return or order..." />{admin && <select className="select-control" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>{['All statuses', 'Submitted', 'Needs inspection', 'Inspected', 'Approved', 'Rejected'].map((value) => <option key={value}>{value}</option>)}</select>}</Toolbar><DataTable columns={columns} rows={admin ? visible : visible.map(({ customer, ...rest }) => rest)} /></Panel>
    {modal && <Modal title="Raise a return request" onClose={() => setModal(false)}><p className="form-note">Choose a delivered order and tell us what went wrong. This is a frontend-only request.</p><form className="form-stack" onSubmit={(e) => { e.preventDefault(); const data = new FormData(e.currentTarget); setRows((current) => [{ id: `RET-${1025 + current.length}`, order: data.get('order'), customer: 'Aarav Wellness Mart', date: '24 Nov 2026', item: data.get('item'), reason: data.get('reason'), status: 'Submitted' }, ...current]); setModal(false); notify('Return request submitted in demo'); }}><label>Order<select name="order"><option>GR-24078</option><option>GR-24077</option><option>GR-24075</option></select></label><label>Product and quantity<input name="item" required placeholder="e.g. Daily Strength Shampoo · 1 box" /></label><label>Reason for return<textarea name="reason" required rows="3" placeholder="Describe the issue..." /></label><div className="modal-actions"><Button type="button" variant="secondary" onClick={() => setModal(false)}>Cancel</Button><Button type="submit"><Send size={15} /> Submit request</Button></div></form></Modal>}
  </SectionFrame>;
}

function CartPage() {
  const { cart, setCart, placeOrder, notify, pointsBalance } = useDemo();
  const [usePoints, setUsePoints] = useState(false);
  const [credit, setCredit] = useState(false);
  const [confirm, setConfirm] = useState(false);
  const subtotal = cart.reduce((sum, item) => sum + item.price * item.quantity, 0);
  const maxDiscount = subtotal * 0.2;
  const pointDiscount = usePoints ? Math.min(maxDiscount, pointsBalance / 100) : 0;
  const total = subtotal - pointDiscount;
  const changeQty = (id, value) => setCart((items) => items.map((item) => item.id === id ? { ...item, quantity: Math.min(item.stock, Math.max(1, Number(value) || 1)) } : item));
  const remove = (id) => { setCart((items) => items.filter((item) => item.id !== id)); notify('Item removed from cart'); };
  return <SectionFrame eyebrow="YOUR NEXT ORDER" title="Cart & checkout" description="Orders are submitted for review. Payment processing is not enabled in this demo.">
    {cart.length ? <div className="checkout-layout"><div className="checkout-main"><Panel title={`Your items (${cart.length})`} eyebrow="ORDER ITEMS"><div className="cart-list">{cart.map((item) => <div className="cart-row" key={item.id}><div className={`cart-art art-${item.color}`}>{item.emoji}</div><div className="cart-product"><strong>{item.name}</strong><small>{item.category} · {item.units} units per box</small><span>{money(item.price)} / box</span></div><label className="quantity-field">Boxes<input type="number" min="1" max={item.stock} value={item.quantity} onChange={(e) => changeQty(item.id, e.target.value)} /></label><strong className="cart-line-total">{money(item.price * item.quantity)}</strong><button className="icon-button remove-button" aria-label="Remove item" onClick={() => remove(item.id)}><X size={16} /></button></div>)}</div></Panel>
      <Panel title="Payment preference" eyebrow="HOW WOULD YOU LIKE TO PAY?"><label className={`payment-option ${!credit ? 'payment-selected' : ''}`}><input type="radio" checked={!credit} onChange={() => setCredit(false)} /><span className="payment-option-icon"><Banknote size={18} /></span><span><strong>Advance payment</strong><small>Pay after your order is approved. You’ll receive payment instructions.</small></span><i className="radio-mark" /></label><label className={`payment-option ${credit ? 'payment-selected' : ''}`}><input type="radio" checked={credit} onChange={() => setCredit(true)} /><span className="payment-option-icon"><CreditCard size={18} /></span><span><strong>Use approved credit facility</strong><small>Available credit: ₹1,76,000 · 30-day terms</small></span><i className="radio-mark" /></label>{credit && total > 176000 && <p className="inline-warning">This order is above your available credit. Reduce the order or choose advance payment.</p>}</Panel>
      </div><aside className="checkout-summary panel"><p className="eyebrow">ORDER SUMMARY</p><h2>Almost yours.</h2><div className="summary-lines"><div><span>Subtotal</span><strong>{money(subtotal)}</strong></div><div><span>Boxes in order</span><strong>{cart.reduce((sum, item) => sum + item.quantity, 0)}</strong></div><div><span>Delivery & taxes</span><strong>Calculated after approval</strong></div></div><div className="points-redemption"><label><span><Gift size={16} /><strong>Use your points</strong></span><input type="checkbox" checked={usePoints} disabled={pointsBalance < 1000} onChange={(e) => setUsePoints(e.target.checked)} /></label><small>{fmt(pointsBalance)} points available · max 20% of order</small>{usePoints && <div className="discount-line"><span>Points discount</span><strong>−{money(pointDiscount)}</strong></div>}</div><div className="summary-total"><span>Estimated total</span><strong>{money(total)}</strong><small>Final total may include applicable taxes and delivery.</small></div><Button className="full-button checkout-button" disabled={cart.length === 0 || (credit && total > 176000)} onClick={() => setConfirm(true)}>Submit order for review <ArrowRight size={16} /></Button><p className="summary-safe"><ShieldCheck size={14} /> No payment is taken in this frontend demo.</p></aside></div>
      : <div className="cart-empty panel"><span><ShoppingBag size={24} /></span><h2>Your cart is taking a breather.</h2><p>Browse the catalogue and add products by the box to get started.</p><Link className="button button-primary" to="/wholesaler/products">Explore products <ArrowRight size={15} /></Link></div>}
    {confirm && <Modal title="Confirm demo order" onClose={() => setConfirm(false)}><div className="confirmation-symbol"><ClipboardList size={23} /></div><h3 className="confirm-title">Ready to submit?</h3><p className="form-note">Your order total is <strong>{money(total)}</strong> and the selected preference is <strong>{credit ? 'approved credit' : 'advance payment'}</strong>. This will only create a sample order—no payment is processed.</p><div className="modal-actions"><Button variant="secondary" onClick={() => setConfirm(false)}>Keep reviewing</Button><Button onClick={() => { setConfirm(false); placeOrder({ payment: credit ? 'Credit' : 'Advance', amount: total, pointsUsed: usePoints ? Math.ceil(pointDiscount * 100) : 0 }); }}>Confirm demo order</Button></div></Modal>}
  </SectionFrame>;
}

function MyRewardsPage() {
  const { pointsBalance } = useDemo();
  return <SectionFrame eyebrow="YOUR LOYALTY ACCOUNT" title="My rewards" description="A clear view of what you’ve earned and what’s still on its way.">
    <div className="reward-balance-grid"><div className="balance-card balance-main"><span className="balance-icon"><Gift size={19} /></span><small>AVAILABLE TO REDEEM</small><strong>{fmt(pointsBalance)} <i>pts</i></strong><span>Worth ₹{(pointsBalance / 100).toFixed(2)} at checkout</span></div><div className="balance-card"><small>PENDING POINTS</small><strong>1,200 <i>pts</i></strong><span>Unlock after payment & delivery</span></div><div className="balance-card"><small>POINTS EARNED TO DATE</small><strong>18,650 <i>pts</i></strong><span>Since joining Groomix</span></div></div>
    <div className="reward-info-banner"><Sparkles size={18} /><p><strong>Points expiry:</strong> Points expire 12 months after they’re earned. Your next 600 points expire on 18 Dec 2026.</p><Link to="/wholesaler/rewards-store">Explore Rewards Store <ArrowRight size={14} /></Link></div>
    <Panel title="Points activity" eyebrow="YOUR REWARDS LEDGER"><DataTable columns={[
      { key: 'description', label: 'ACTIVITY', render: (row) => <div className="activity-cell"><span className={`activity-icon ${row.points > 0 ? 'earned' : 'spent'}`}>{row.points > 0 ? <Sparkles size={15} /> : <Gift size={15} />}</span><span><strong>{row.description}</strong><small>{row.date}</small></span></div> },
      { key: 'order', label: 'REFERENCE' }, { key: 'status', label: 'STATUS', render: (row) => <StatusPill value={row.status} /> }, { key: 'points', label: 'POINTS', render: (row) => <strong className={row.points > 0 ? 'points-positive' : 'points-negative'}>{row.points > 0 ? '+' : ''}{fmt(row.points)} pts</strong> },
    ]} rows={[
      { id: 'a', description: 'Order delivered · Daily essentials', date: '18 Nov 2026', order: 'GR-24077', status: 'Available', points: 1200 },
      { id: 'b', description: 'Order delivered · Hair care', date: '12 Nov 2026', order: 'GR-24073', status: 'Available', points: 850 },
      { id: 'c', description: 'Groomix Travel Pouch', date: '08 Nov 2026', order: 'RD-0338', status: 'Redeemed', points: -6500 },
      { id: 'd', description: 'Order delivered · Face care', date: '03 Nov 2026', order: 'GR-24069', status: 'Available', points: 640 },
      { id: 'e', description: 'Order payment received', date: '02 Nov 2026', order: 'GR-24066', status: 'Pending', points: 1200 },
    ]} /></Panel>
  </SectionFrame>;
}

function ReportsPage() {
  const [range, setRange] = useState('This month');
  const [report, setReport] = useState('Sales overview');
  const reportData = {
    'Sales overview': {
      metrics: [['Gross sales', '₹18,42,600', '↑ 12.8% vs previous period'], ['Est. gross profit', '₹5,64,200', 'Based on sample manufacturing costs'], ['Orders fulfilled', '186', '↑ 8.4% vs previous period'], ['Rewards issued', '2,46,800 pts', '₹2,468 estimated redemption value']],
      chart: 'Monthly sales', list: 'Top products', listLabel: 'BY WHOLESALE SALES',
    },
    'Product performance': {
      metrics: [['Best-selling product', 'Shampoo', 'Daily Strength · 320 boxes'], ['Product sales', '₹3,84,000', 'Top product this period'], ['Active products', '14', 'Across 4 categories'], ['Low-stock products', '03', 'Review replenishment']],
      chart: 'Sales by category', list: 'Product leaders', listLabel: 'BY BOXES SOLD',
    },
    'Profit overview': {
      metrics: [['Estimated gross profit', '₹5,64,200', 'Based on sample manufacturing costs'], ['Gross margin', '30.6%', 'Weighted average estimate'], ['Manufacturing costs', '₹12,78,400', 'Sample product cost snapshots'], ['Rewards budget', '₹56,420', '10% of estimated gross profit']],
      chart: 'Estimated profit trend', list: 'Margin leaders', listLabel: 'ESTIMATED GROSS MARGIN',
    },
    'Loyalty rewards': {
      metrics: [['Points issued', '2,46,800', '↑ 6.1% this month'], ['Points redeemed', '84,500', 'Across checkout & store'], ['Pending points', '32,400', 'Awaiting full payment & delivery'], ['Reward redemptions', '38', 'Store requests this month']],
      chart: 'Points activity', list: 'Popular rewards', listLabel: 'BY REDEMPTIONS',
    },
    'Payments & credit': {
      metrics: [['Payments verified', '₹12,48,600', 'This month'], ['Awaiting verification', '₹2,14,800', '08 payments to review'], ['Outstanding credit', '₹6,84,000', 'Across 34 active accounts'], ['Overdue accounts', '03', 'Follow-up recommended']],
      chart: 'Verified payments', list: 'Credit utilization', listLabel: 'ACTIVE FACILITIES',
    },
  };
  const currentReport = reportData[report];
  return <SectionFrame eyebrow="BUSINESS INTELLIGENCE" title="Reports" description="A useful overview of sales, margins and customer rewards." action={<button className="button button-secondary" onClick={() => window.alert('Report download is a demo action.')}><Download size={15} /> Export report</button>}>
    <div className="report-tabs">{Object.keys(reportData).map((item) => <button key={item} className={report === item ? 'report-tab-active' : ''} onClick={() => setReport(item)}>{item}</button>)}</div>
    <div className="report-filter-row"><span>Showing sample data for</span><select className="select-control" value={range} onChange={(e) => setRange(e.target.value)}><option>This month</option><option>Last month</option><option>Last 90 days</option><option>This year</option></select><span className="muted-text">· Data is illustrative, not actual business records</span></div>
    <div className="report-kpis">{currentReport.metrics.map(([label, value, note]) => <div key={label}><small>{label}</small><strong>{value}</strong><span>{note}</span></div>)}</div>
    <div className="reports-grid"><Panel title={currentReport.chart} eyebrow={report.toUpperCase()}><div className="report-bars">{[42, 56, 49, 74, 66, 88, 61, 77, 58, 82, 69, 94].map((height, index) => <div key={index}><span style={{ height: `${height}%` }} /><small>{['D', 'J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N'][index]}</small></div>)}</div></Panel><Panel title={currentReport.list} eyebrow={currentReport.listLabel}><div className="top-product-list">{[['Daily Strength Shampoo', '₹3,84,000', 90], ['Daily Reset Face Wash', '₹2,64,000', 72], ['Sunveil SPF 50 Sunscreen', '₹1,92,000', 55], ['Fresh Start Body Wash', '₹1,56,000', 44]].map(([name, value, width], i) => <div className="top-product" key={name}><span className="rank">{String(i + 1).padStart(2, '0')}</span><div><strong>{name}</strong><div className="thin-progress"><i style={{ width: `${width}%` }} /></div></div><b>{value}</b></div>)}</div></Panel></div>
  </SectionFrame>;
}

function ProfilePage({ admin }) {
  const { session, notify } = useDemo();
  return <SectionFrame eyebrow="ACCOUNT PREFERENCES" title={admin ? 'Settings' : 'Business profile'} description={admin ? 'Manage your profile and basic business preferences.' : 'Keep your contact and business information up to date.'}>
    <div className="profile-layout"><div className="profile-main"><Panel title="Business details" eyebrow="YOUR ORGANIZATION"><form className="form-grid" onSubmit={(e) => { e.preventDefault(); notify('Profile saved in demo'); }}><label>Business name<input defaultValue={admin ? 'Groomix Personal Care Pvt. Ltd.' : 'Aarav Wellness Mart'} /></label><label>Business type<select defaultValue="Wholesale / Retail"><option>Wholesale / Retail</option><option>Retail</option><option>Distributor</option></select></label><label>GSTIN (optional)<input defaultValue={admin ? '27AABCG1234A1Z5' : '27AAXXX1234A1Z2'} /></label><label>Contact email<input type="email" defaultValue={admin ? 'hello@groomix.example' : 'aarav@wellnessmart.example'} /></label><label>Contact phone<input type="tel" defaultValue="+91 98765 43210" /></label><label>Contact person<input defaultValue={session?.name} /></label><label className="field-span">Business address<textarea rows="3" defaultValue={admin ? 'Groomix House, Andheri East, Mumbai, Maharashtra 400069' : '12 Market Road, Koregaon Park, Pune, Maharashtra 411001'} /></label><div className="field-span form-actions"><Button type="submit">Save changes</Button></div></form></Panel>
      {admin && <Panel title="Business preferences" eyebrow="REGIONAL SETTINGS"><form className="form-grid" onSubmit={(e) => { e.preventDefault(); notify('Business preferences saved in demo'); }}><label>Business currency<select defaultValue="INR (₹)"><option>INR (₹)</option></select></label><label>Time zone<select defaultValue="Asia/Kolkata"><option>Asia/Kolkata (IST)</option></select></label><label>Default payment terms<select defaultValue="30 days"><option>Advance payment</option><option>15 days</option><option>30 days</option><option>45 days</option></select></label><div className="field-span form-actions"><Button type="submit" variant="secondary"><Settings2 size={15} /> Save preferences</Button></div></form></Panel>}</div>
      <aside className="profile-aside"><div className="profile-card"><span className="profile-avatar profile-avatar-xl">{admin ? 'RK' : 'AW'}</span><h3>{session?.name}</h3><p>{admin ? 'Factory Admin' : 'Verified wholesale partner'}</p><span className="profile-verified"><ShieldCheck size={14} /> {admin ? 'Administrator' : 'Business profile active'}</span></div><div className="aside-note"><MapPin size={17} /><p><strong>Business location</strong><br />{admin ? 'Mumbai, Maharashtra' : 'Pune, Maharashtra'}</p></div><div className="aside-note"><ShieldCheck size={17} /><p><strong>Demo workspace</strong><br />Changes stay in this browser session.</p></div></aside></div>
  </SectionFrame>;
}

export default function WorkspacePage({ section: sectionProp }) {
  const { session } = useDemo();
  const { section: routeSection } = useParams();
  const role = session?.role || 'admin';
  const section = sectionProp || routeSection;
  if (section === 'cart') return <CartPage />;
  if (section === 'categories' && role === 'admin') return <CategoriesPage />;
  if (section === 'wholesalers' && role === 'admin') return <WholesalersPage />;
  if (section === 'orders') return <OrdersPage />;
  if (section === 'payments-credit') return <CreditPaymentPage />;
  if (section === 'loyalty' && role === 'admin') return <LoyaltyPage />;
  if (section === 'my-rewards' && role !== 'admin') return <MyRewardsPage />;
  if (section === 'rewards-store') return <RewardsStorePage />;
  if (section === 'returns') return <ReturnsPage />;
  if (section === 'reports' && role === 'admin') return <ReportsPage />;
  if (section === 'settings' || section === 'profile') return <ProfilePage admin={role === 'admin'} />;
  return <NotAvailable />;
}

function NotAvailable() {
  return <div className="page-wrap"><div className="empty-page panel"><span><Box size={24} /></span><h1>This page is not available for this role.</h1><p>Use the sidebar to return to a section in your workspace.</p></div></div>;
}
