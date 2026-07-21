import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import api from '../../api/axiosConfig';
import { Mail, Lock, ArrowRight } from 'lucide-react';
import { toast } from 'react-toastify';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await api.post('/api/auth/login', { email, plain_password: password });
      
      // Get user info with token
      const meResponse = await api.get('/api/auth/me', {
        headers: { Authorization: `Bearer ${response.data.access_token}` }
      });
      
      login(response.data.access_token, meResponse.data);
      toast.success('¡Bienvenido de vuelta!');
      navigate('/');
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Error al iniciar sesión');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background bg-[url('https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?auto=format&fit=crop&q=80')] bg-cover bg-center">
      <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" />

      <style>{`
        @keyframes panelRise {
          from { opacity: 0; transform: translateY(14px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .panel-enter { animation: panelRise 0.5s cubic-bezier(0.16, 1, 0.3, 1) both; }
      `}</style>

      <div className="panel-enter glass-panel p-7 sm:p-9 rounded-2xl w-full max-w-md relative z-10 mx-4 border border-white/30 shadow-2xl shadow-black/30">
        <div className="text-center mb-8">
          {/* Marca de firma: línea de horizonte + punto de ruta */}
          <div className="w-14 h-14 mx-auto mb-5 relative">
            <svg viewBox="0 0 56 56" className="w-full h-full">
              <path
                d="M4 34c8-10 18-14 24-14s16 4 24 14"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                className="text-primary/70"
              />
              <circle cx="28" cy="20" r="4" className="fill-primary" />
              <circle cx="28" cy="20" r="7" fill="none" stroke="currentColor" strokeWidth="1" className="text-primary/40" />
            </svg>
          </div>

          <p className="text-[11px] uppercase tracking-[0.25em] text-foreground/60 font-medium mb-1">
            Orizon Routes
          </p>
          <h2 className="text-3xl font-bold text-foreground tracking-tight">Iniciar Sesión</h2>
          <p className="text-foreground/70 text-sm mt-2">Ingresa a tu cuenta para continuar tu ruta</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-sm font-medium text-foreground/80 mb-1.5">Email</label>
            <div className="relative group">
              <Mail className="w-4.5 h-4.5 absolute left-3.5 top-1/2 -translate-y-1/2 text-foreground/40 group-focus-within:text-primary transition-colors" />
              <input
                type="email"
                required
                autoComplete="email"
                className="w-full pl-10 pr-4 py-2.5 bg-white/60 border border-white/50 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/60 focus:border-primary/60 focus:bg-white/80 transition-all duration-200 text-foreground placeholder:text-foreground/40 shadow-sm"
                placeholder="tu@email.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-foreground/80 mb-1.5">Contraseña</label>
            <div className="relative group">
              <Lock className="w-4.5 h-4.5 absolute left-3.5 top-1/2 -translate-y-1/2 text-foreground/40 group-focus-within:text-primary transition-colors" />
              <input
                type="password"
                required
                autoComplete="current-password"
                className="w-full pl-10 pr-4 py-2.5 bg-white/60 border border-white/50 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/60 focus:border-primary/60 focus:bg-white/80 transition-all duration-200 text-foreground placeholder:text-foreground/40 shadow-sm"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
          </div>

          <button
            type="submit"
            className="w-full group bg-gradient-to-r from-primary to-secondary hover:brightness-110 active:scale-[0.98] text-white font-medium py-2.5 px-4 rounded-xl transition-all duration-200 cursor-pointer mt-2 shadow-lg shadow-primary/30 hover:shadow-primary/40 hover:-translate-y-0.5 flex items-center justify-center gap-2"
          >
            Entrar
            <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-0.5" />
          </button>
        </form>

        <p className="text-center text-sm text-foreground/70 mt-7">
          ¿No tienes cuenta?{' '}
          <Link to="/register" className="text-primary hover:text-accent font-medium transition-colors">
            Regístrate
          </Link>
        </p>
      </div>
    </div>
  );
}