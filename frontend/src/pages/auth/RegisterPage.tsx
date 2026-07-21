import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../../api/axiosConfig';
import { Mail, Lock, User as UserIcon, Shield, ChevronDown, ArrowRight } from 'lucide-react';
import { toast } from 'react-toastify';

export default function RegisterPage() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    plain_password: '',
    role: 'pasajero'
  });
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/api/auth/register', formData);
      toast.success('¡Registro exitoso! Ahora inicia sesión.');
      navigate('/login');
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Error al registrarse');
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
                className="text-accent/70"
              />
              <circle cx="28" cy="20" r="4" className="fill-accent" />
              <circle cx="28" cy="20" r="7" fill="none" stroke="currentColor" strokeWidth="1" className="text-accent/40" />
            </svg>
          </div>

          <p className="text-[11px] uppercase tracking-[0.25em] text-foreground/60 font-medium mb-1">
            Orizon Routes
          </p>
          <h2 className="text-3xl font-bold text-foreground tracking-tight">Crear Cuenta</h2>
          <p className="text-foreground/70 text-sm mt-2">Únete a Orizon Routes hoy mismo</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-sm font-medium text-foreground/80 mb-1.5">Nombre Completo</label>
            <div className="relative group">
              <UserIcon className="w-4.5 h-4.5 absolute left-3.5 top-1/2 -translate-y-1/2 text-foreground/40 group-focus-within:text-accent transition-colors" />
              <input
                type="text"
                required
                autoComplete="name"
                className="w-full pl-10 pr-4 py-2.5 bg-white/60 border border-white/50 rounded-xl focus:outline-none focus:ring-2 focus:ring-accent/60 focus:border-accent/60 focus:bg-white/80 transition-all duration-200 text-foreground placeholder:text-foreground/40 shadow-sm"
                placeholder="Juan Pérez"
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-foreground/80 mb-1.5">Email</label>
            <div className="relative group">
              <Mail className="w-4.5 h-4.5 absolute left-3.5 top-1/2 -translate-y-1/2 text-foreground/40 group-focus-within:text-accent transition-colors" />
              <input
                type="email"
                required
                autoComplete="email"
                className="w-full pl-10 pr-4 py-2.5 bg-white/60 border border-white/50 rounded-xl focus:outline-none focus:ring-2 focus:ring-accent/60 focus:border-accent/60 focus:bg-white/80 transition-all duration-200 text-foreground placeholder:text-foreground/40 shadow-sm"
                placeholder="tu@email.com"
                value={formData.email}
                onChange={(e) => setFormData({...formData, email: e.target.value})}
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-foreground/80 mb-1.5">Contraseña</label>
            <div className="relative group">
              <Lock className="w-4.5 h-4.5 absolute left-3.5 top-1/2 -translate-y-1/2 text-foreground/40 group-focus-within:text-accent transition-colors" />
              <input
                type="password"
                required
                autoComplete="new-password"
                className="w-full pl-10 pr-4 py-2.5 bg-white/60 border border-white/50 rounded-xl focus:outline-none focus:ring-2 focus:ring-accent/60 focus:border-accent/60 focus:bg-white/80 transition-all duration-200 text-foreground placeholder:text-foreground/40 shadow-sm"
                placeholder="••••••••"
                value={formData.plain_password}
                onChange={(e) => setFormData({...formData, plain_password: e.target.value})}
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-foreground/80 mb-1.5">¿Cómo usarás la app?</label>
            <div className="relative group">
              <Shield className="w-4.5 h-4.5 absolute left-3.5 top-1/2 -translate-y-1/2 text-foreground/40 group-focus-within:text-accent transition-colors z-10" />
              <select
                className="w-full pl-10 pr-9 py-2.5 bg-white/60 border border-white/50 rounded-xl focus:outline-none focus:ring-2 focus:ring-accent/60 focus:border-accent/60 focus:bg-white/80 transition-all duration-200 text-foreground cursor-pointer appearance-none shadow-sm"
                value={formData.role}
                onChange={(e) => setFormData({...formData, role: e.target.value})}
              >
                <option value="pasajero">Soy Pasajero</option>
                <option value="conductor">Soy Conductor</option>
              </select>
              <ChevronDown className="w-4 h-4 absolute right-3.5 top-1/2 -translate-y-1/2 text-foreground/40 pointer-events-none" />
            </div>
          </div>

          <button
            type="submit"
            className="w-full group bg-gradient-to-r from-accent to-orange-600 hover:brightness-110 active:scale-[0.98] text-white font-medium py-2.5 px-4 rounded-xl transition-all duration-200 cursor-pointer mt-2 shadow-lg shadow-accent/30 hover:shadow-accent/40 hover:-translate-y-0.5 flex items-center justify-center gap-2"
          >
            Registrarme
            <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-0.5" />
          </button>
        </form>

        <p className="text-center text-sm text-foreground/70 mt-7">
          ¿Ya tienes cuenta?{' '}
          <Link to="/login" className="text-primary hover:text-accent font-medium transition-colors">
            Inicia sesión
          </Link>
        </p>
      </div>
    </div>
  );
}