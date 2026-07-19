import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../../api/axiosConfig';
import { UserPlus, Mail, Lock, User as UserIcon, Shield } from 'lucide-react';
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
      await api.post('/auth/register', formData);
      toast.success('¡Registro exitoso! Ahora inicia sesión.');
      navigate('/login');
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Error al registrarse');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background bg-[url('https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?auto=format&fit=crop&q=80')] bg-cover bg-center">
      <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" />
      
      <div className="glass-panel p-8 rounded-2xl w-full max-w-md relative z-10 mx-4">
        <div className="text-center mb-8">
          <div className="bg-accent/10 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
            <UserPlus className="w-8 h-8 text-accent" />
          </div>
          <h2 className="text-2xl font-bold text-foreground">Crear Cuenta</h2>
          <p className="text-foreground/70 text-sm mt-2">Únete a Orizon Routes hoy mismo</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-foreground/80 mb-1">Nombre Completo</label>
            <div className="relative">
              <UserIcon className="w-5 h-5 absolute left-3 top-1/2 -translate-y-1/2 text-foreground/50" />
              <input 
                type="text" 
                required
                className="w-full pl-10 pr-4 py-2 bg-white/50 border border-white/40 rounded-lg focus:outline-none focus:ring-2 focus:ring-accent transition-all text-foreground"
                placeholder="Juan Pérez"
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-foreground/80 mb-1">Email</label>
            <div className="relative">
              <Mail className="w-5 h-5 absolute left-3 top-1/2 -translate-y-1/2 text-foreground/50" />
              <input 
                type="email" 
                required
                className="w-full pl-10 pr-4 py-2 bg-white/50 border border-white/40 rounded-lg focus:outline-none focus:ring-2 focus:ring-accent transition-all text-foreground"
                placeholder="tu@email.com"
                value={formData.email}
                onChange={(e) => setFormData({...formData, email: e.target.value})}
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-foreground/80 mb-1">Contraseña</label>
            <div className="relative">
              <Lock className="w-5 h-5 absolute left-3 top-1/2 -translate-y-1/2 text-foreground/50" />
              <input 
                type="password" 
                required
                className="w-full pl-10 pr-4 py-2 bg-white/50 border border-white/40 rounded-lg focus:outline-none focus:ring-2 focus:ring-accent transition-all text-foreground"
                placeholder="••••••••"
                value={formData.plain_password}
                onChange={(e) => setFormData({...formData, plain_password: e.target.value})}
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-foreground/80 mb-1">¿Cómo usarás la app?</label>
            <div className="relative">
              <Shield className="w-5 h-5 absolute left-3 top-1/2 -translate-y-1/2 text-foreground/50" />
              <select 
                className="w-full pl-10 pr-4 py-2 bg-white/50 border border-white/40 rounded-lg focus:outline-none focus:ring-2 focus:ring-accent transition-all text-foreground cursor-pointer appearance-none"
                value={formData.role}
                onChange={(e) => setFormData({...formData, role: e.target.value})}
              >
                <option value="pasajero">Soy Pasajero</option>
                <option value="conductor">Soy Conductor</option>
              </select>
            </div>
          </div>

          <button 
            type="submit" 
            className="w-full bg-accent hover:bg-orange-600 text-white font-medium py-2 px-4 rounded-lg transition-colors cursor-pointer duration-200 mt-6 shadow-lg shadow-accent/30"
          >
            Registrarme
          </button>
        </form>

        <p className="text-center text-sm text-foreground/70 mt-6">
          ¿Ya tienes cuenta? <Link to="/login" className="text-primary hover:text-accent font-medium transition-colors">Inicia sesión</Link>
        </p>
      </div>
    </div>
  );
}
