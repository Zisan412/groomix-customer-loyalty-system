import { createContext, useContext, useMemo, useState } from 'react';
import { Navigate, Route, Routes, useNavigate, useParams } from 'react-router-dom';
import AuthPage from './pages/auth/AuthPage.jsx';
import WorkspaceLayout from './layouts/WorkspaceLayout.jsx';
import DashboardPage from './pages/DashboardPage.jsx';
import CatalogPage from './pages/CatalogPage.jsx';
import WorkspacePage from './pages/WorkspacePage.jsx';
import { orders as initialOrders, products as initialProducts } from './data/demoData.js';

const AppContext = createContext(null);
export const useDemo = () => useContext(AppContext);

function ProtectedWorkspace() {
  const { session } = useDemo();
  const { role } = useParams();
  if (!session) return <Navigate to="/login" replace />;
  if (role && role !== session.role) return <Navigate to={`/${session.role}/overview`} replace />;
  return <WorkspaceLayout />;
}

function AuthRoute({ mode }) {
  const { signIn } = useDemo();
  const navigate = useNavigate();
  return <AuthPage mode={mode} onSignIn={(role) => { signIn(role); navigate(`/${role}/overview`); }} />;
}

export default function App() {
  const [session, setSession] = useState(() => {
    try { return JSON.parse(localStorage.getItem('groomix-demo-session')); } catch { return null; }
  });
  const [products, setProducts] = useState(initialProducts);
  const [orders, setOrders] = useState(initialOrders);
  const [cart, setCart] = useState([]);
  const [pointsBalance, setPointsBalance] = useState(8450);
  const [toast, setToast] = useState('');
  const signIn = (role) => {
    const next = { role, name: role === 'admin' ? 'Rhea Kapoor' : 'Aarav Wellness Mart' };
    setSession(next);
    localStorage.setItem('groomix-demo-session', JSON.stringify(next));
  };
  const signOut = () => { setSession(null); localStorage.removeItem('groomix-demo-session'); setCart([]); };
  const notify = (message) => { setToast(message); window.setTimeout(() => setToast(''), 2800); };
  const addToCart = (product, quantity = 1) => {
    setCart((items) => {
      const current = items.find((item) => item.id === product.id);
      return current ? items.map((item) => item.id === product.id ? { ...item, quantity: item.quantity + quantity } : item) : [...items, { ...product, quantity }];
    });
    notify(`${product.name} added to cart`);
  };
  const updateProduct = (product) => {
    setProducts((items) => items.some((item) => item.id === product.id)
      ? items.map((item) => item.id === product.id ? product : item)
      : [{ ...product, id: Math.max(...items.map((item) => item.id)) + 1 }, ...items]);
    notify('Product saved in this demo');
  };
  const placeOrder = ({ payment = 'Advance', amount, pointsUsed = 0 } = {}) => {
    const total = amount ?? cart.reduce((sum, item) => sum + item.price * item.quantity, 0);
    setOrders((items) => [{
      id: `GR-${24100 + items.length}`, wholesaler: session?.name || 'Aarav Wellness Mart',
      date: '24 Nov 2026', amount: total, status: 'Pending approval', payment,
      pointsUsed,
      items: cart.reduce((sum, item) => sum + item.quantity, 0),
    }, ...items]);
    if (pointsUsed > 0) setPointsBalance((balance) => Math.max(0, balance - pointsUsed));
    setCart([]);
    notify('Demo order placed. No payment was processed.');
  };
  const updateOrderStatus = (orderId, status) => {
    const order = orders.find((item) => item.id === orderId);
    setOrders((items) => items.map((item) => item.id === orderId ? { ...item, status } : item));
    if (status === 'Cancelled' && order?.pointsUsed) {
      setPointsBalance((balance) => balance + order.pointsUsed);
    }
  };
  const value = useMemo(() => ({ session, signIn, signOut, products, updateProduct, orders, updateOrderStatus, cart, setCart, addToCart, placeOrder, pointsBalance, setPointsBalance, notify }), [session, products, orders, cart, pointsBalance]);
  return (
    <AppContext.Provider value={value}>
      <Routes>
        <Route path="/login" element={<AuthRoute mode="login" />} />
        <Route path="/register" element={<AuthRoute mode="register" />} />
        <Route path="/forgot-password" element={<AuthRoute mode="forgot" />} />
        <Route element={<ProtectedWorkspace />}>
          <Route path="/:role/overview" element={<DashboardPage />} />
          <Route path="/:role/products" element={<CatalogPage />} />
          <Route path="/:role/cart" element={<WorkspacePage section="cart" />} />
          <Route path="/:role/:section" element={<WorkspacePage />} />
          <Route path="/" element={<Navigate to={session ? `/${session.role}/overview` : '/login'} replace />} />
        </Route>
        <Route path="*" element={<Navigate to={session ? `/${session.role}/overview` : '/login'} replace />} />
      </Routes>
      {toast && <div className="toast" role="status">{toast}</div>}
    </AppContext.Provider>
  );
}
