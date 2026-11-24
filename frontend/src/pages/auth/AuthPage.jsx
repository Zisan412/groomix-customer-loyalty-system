import { useState } from 'react';
import { ArrowLeft, ArrowRight, Leaf, LockKeyhole, Mail, Store } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Button } from '../../components/UI.jsx';

export default function AuthPage({ mode, onSignIn }) {
  const [role, setRole] = useState('admin');
  const [message, setMessage] = useState('');
  const [form, setForm] = useState({ name: '', email: '', password: '', business: '' });
  const isRegister = mode === 'register';
  const isForgot = mode === 'forgot';
  const submit = (event) => {
    event.preventDefault();
    if (isForgot) { setMessage('If this email is registered, reset instructions would be sent.'); return; }
    if (isRegister) { setMessage('Demo wholesaler account created. No real account was registered.'); onSignIn('wholesaler'); return; }
    onSignIn(role);
  };
  return <main className="auth-page">
    <section className="auth-visual"><Link to="/login" className="brand brand-light"><span className="brand-mark"><Leaf size={18} /></span>groomix</Link>
      <div className="auth-visual-copy"><span className="auth-kicker">GROOMIX WHOLESALE PARTNER</span><h1>Good business.<br />Better care.</h1><p>A simpler way to grow your personal-care business, with rewards that give back.</p>
        <div className="visual-stat"><div className="avatar-stack"><span>AW</span><span>DE</span><span>UG</span></div><span>Made for growing businesses</span></div>
      </div><span className="visual-caption">THOUGHTFULLY MADE. PURPOSEFULLY GROWN.</span>
    </section>
    <section className="auth-form-side"><div className="auth-mobile-brand"><Link to="/login" className="brand"><span className="brand-mark"><Leaf size={18} /></span>groomix</Link></div>
      <div className="auth-form-wrap">
        <p className="eyebrow">{isRegister ? 'JOIN OUR PARTNER NETWORK' : isForgot ? 'ACCOUNT SUPPORT' : 'WELCOME BACK'}</p>
        <h2>{isRegister ? 'Create your account' : isForgot ? 'Reset your password' : 'Sign in to Groomix'}</h2>
        <p className="auth-lead">{isRegister ? 'A few details to get your business started.' : isForgot ? 'Enter your email and we’ll show a demo confirmation.' : 'Your wholesale workspace is ready when you are.'}</p>
        {mode === 'login' && <div className="role-select" aria-label="Choose demo role">
          <button type="button" className={role === 'admin' ? 'selected' : ''} onClick={() => setRole('admin')}><LockKeyhole size={16} />Factory Admin</button>
          <button type="button" className={role === 'wholesaler' ? 'selected' : ''} onClick={() => setRole('wholesaler')}><Store size={16} />Wholesaler</button>
        </div>}
        <form className="form-stack" onSubmit={submit}>
          {isRegister && <><label>Contact name<input required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="Your full name" /></label><label>Business name<input required value={form.business} onChange={(e) => setForm({ ...form, business: e.target.value })} placeholder="Your store or business" /></label></>}
          <label>Email address<span className="input-icon"><Mail size={16} /><input type="email" required value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} placeholder="you@business.com" /></span></label>
          {!isForgot && <label>Password<span className="input-icon"><LockKeyhole size={16} /><input type="password" minLength="6" required value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} placeholder="At least 6 characters" /></span></label>}
          {!isRegister && !isForgot && <div className="form-inline"><label className="checkbox-line"><input type="checkbox" /> Remember me</label><Link to="/forgot-password">Forgot password?</Link></div>}
          <Button type="submit" className="full-button">{isRegister ? 'Create demo account' : isForgot ? 'Show reset confirmation' : 'Continue'} <ArrowRight size={16} /></Button>
          {message && <p className="inline-message">{message}</p>}
        </form>
        <p className="auth-switch">{isRegister ? 'Already a partner?' : 'New to Groomix?'} <Link to={isRegister ? '/login' : '/register'}>{isRegister ? 'Sign in' : 'Create an account'}</Link></p>
        <p className="demo-note">Frontend demonstration only · No real authentication or payments</p>
        {isForgot && <Link className="back-link" to="/login"><ArrowLeft size={15} /> Back to sign in</Link>}
      </div>
    </section>
  </main>;
}
