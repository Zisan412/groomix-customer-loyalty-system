import { useMemo, useState } from 'react';
import { ArrowDownUp, Package, Plus, ShoppingBag, SlidersHorizontal } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useDemo } from '../App.jsx';
import { Button, PageHeader, SearchBox } from '../components/UI.jsx';
import { categories } from '../data/demoData.js';

const money = (value) => `₹${Number(value).toLocaleString('en-IN')}`;

export default function CatalogPage() {
  const { session, products, addToCart, updateProduct } = useDemo();
  const admin = session?.role === 'admin';
  const [query, setQuery] = useState('');
  const [category, setCategory] = useState('All products');
  const [sort, setSort] = useState('featured');
  const [editing, setEditing] = useState(null);
  const filtered = useMemo(() => products.filter((item) => (category === 'All products' || item.category === category) && `${item.name} ${item.category} ${item.sku}`.toLowerCase().includes(query.toLowerCase()))
    .sort((a, b) => sort === 'price-low' ? a.price - b.price : sort === 'price-high' ? b.price - a.price : a.id - b.id), [products, category, query, sort]);
  const save = (event) => {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    updateProduct({ ...editing, name: data.get('name'), category: data.get('category'), sku: data.get('sku'), price: Number(data.get('price')), cost: Number(data.get('cost')), units: Number(data.get('units')), stock: Number(data.get('stock')), status: data.get('status') });
    setEditing(null);
  };
  return <div className="page-wrap">
    <PageHeader eyebrow={admin ? 'CATALOGUE MANAGEMENT' : 'GROOMIX WHOLESALE CATALOGUE'} title={admin ? 'Products' : 'Find your next bestseller'} description={admin ? 'Manage your product range, pricing and available stock.' : 'Thoughtfully made essentials, ready for your shelves.'}
      action={admin ? <Button onClick={() => setEditing({ name: '', category: 'Face Care', price: 0, cost: 0, units: 24, stock: 0, sku: `GM-${Date.now().toString().slice(-4)}`, emoji: '🧴', color: 'sage' })}><Plus size={16} /> Add product</Button> : <Link className="button button-secondary" to="/wholesaler/cart"><ShoppingBag size={16} /> View cart</Link>} />
    <div className="catalog-toolbar"><SearchBox value={query} onChange={setQuery} placeholder="Search products or SKU..." /><div className="filter-control"><SlidersHorizontal size={15} /><select aria-label="Filter by category" value={category} onChange={(e) => setCategory(e.target.value)}>{categories.map((item) => <option key={item}>{item}</option>)}</select></div><div className="filter-control"><ArrowDownUp size={15} /><select aria-label="Sort products" value={sort} onChange={(e) => setSort(e.target.value)}><option value="featured">Featured</option><option value="price-low">Price: low to high</option><option value="price-high">Price: high to low</option></select></div><span className="result-count">{filtered.length} products</span></div>
    <div className="category-chips">{categories.map((item) => <button key={item} className={category === item ? 'chip chip-active' : 'chip'} onClick={() => setCategory(item)}>{item}</button>)}</div>
    <div className="product-grid">{filtered.map((product) => <article className="product-card" key={product.id}>
      <div className={`product-art art-${product.color}`}><span className="product-emoji">{product.emoji}</span>{product.tag && <span className="product-tag">{product.tag}</span>}<span className="art-caption">GROOMIX</span></div>
      <div className="product-card-body"><span className="product-category">{product.category}</span><h3>{product.name}</h3><p className="product-sku">{product.sku} · {product.units} units per box</p>
        <div className="product-price-row"><div><strong>{money(product.price)}</strong><span>per box</span></div>{admin && <span className="stock-label">{product.stock} boxes in stock</span>}</div>
        {admin ? <><div className="admin-product-status"><span>{product.status || 'Active'}</span><span>{Math.floor((product.price - product.cost) / product.price * 100)}% gross margin</span></div><Button variant="secondary" className="full-button" onClick={() => setEditing(product)}>Edit product</Button></> : <Button className="full-button" disabled={product.stock < 1} onClick={() => addToCart(product)}><Plus size={16} /> Add one box</Button>}
      </div></article>)}</div>
    {!filtered.length && <div className="empty-state">No products match your search. Try another name or category.</div>}
    {editing && <div className="modal-backdrop" onMouseDown={(e) => e.target === e.currentTarget && setEditing(null)}><section className="modal"><div className="modal-heading"><h2>{editing.id ? 'Edit product' : 'Add product'}</h2><button className="icon-button" onClick={() => setEditing(null)}>×</button></div><p className="form-note">Changes are saved in this browser demo only.</p><form className="form-grid" onSubmit={save}>
      <label className="field-span">Product name<input name="name" required defaultValue={editing.name} placeholder="Product name" /></label>
      <label>Category<select name="category" defaultValue={editing.category}>{categories.slice(1).map((item) => <option key={item}>{item}</option>)}</select></label>
      <label>SKU<input name="sku" required defaultValue={editing.sku} /></label>
      <label>Wholesale price (₹)<input type="number" min="0" name="price" required defaultValue={editing.price} /></label>
      <label>Manufacturing cost (₹)<input type="number" min="0" name="cost" required defaultValue={editing.cost} /></label>
      <label>Units per box<input type="number" min="1" name="units" required defaultValue={editing.units} /></label>
      <label>Stock (boxes)<input type="number" min="0" name="stock" required defaultValue={editing.stock} /></label>
      <label>Status<select name="status" defaultValue={editing.status || 'Active'}><option>Active</option><option>Paused</option></select></label>
      <div className="field-span form-actions"><Button type="button" variant="secondary" onClick={() => setEditing(null)}>Cancel</Button><Button type="submit"><Package size={15} /> Save product</Button></div>
    </form></section></div>}
  </div>;
}
