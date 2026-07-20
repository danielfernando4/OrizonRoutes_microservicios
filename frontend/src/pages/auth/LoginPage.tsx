import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import api from '../../api/axiosConfig';
import { LogIn, Mail, Lock } from 'lucide-react';
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
      
      <div className="glass-panel p-8 rounded-2xl w-full max-w-md relative z-10 mx-4">
        <div className="text-center mb-8">
          <div className="bg-primary/10 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
            <LogIn className="w-8 h-8 text-primary" />
          </div>
          <h2 className="text-2xl font-bold text-foreground">Iniciar Sesión</h2>
          <p className="text-foreground/70 text-sm mt-2">Ingresa a tu cuenta de Orizon Routes</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-foreground/80 mb-1">Email</label>
            <div className="relative">
              <Mail className="w-5 h-5 absolute left-3 top-1/2 -translate-y-1/2 text-foreground/50" />
              <input 
                type="email" 
                required
                className="w-full pl-10 pr-4 py-2 bg-white/50 border border-white/40 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary transition-all text-foreground placeholder:text-foreground/50"
                placeholder="tu@email.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
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
                className="w-full pl-10 pr-4 py-2 bg-white/50 border border-white/40 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary transition-all text-foreground placeholder:text-foreground/50"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
          </div>

          <button 
            type="submit" 
            className="w-full bg-primary hover:bg-secondary text-white font-medium py-2 px-4 rounded-lg transition-colors cursor-pointer duration-200 mt-6 shadow-lg shadow-primary/30"
          >
            Entrar
          </button>
        </form>

        <p className="text-center text-sm text-foreground/70 mt-6">
          ¿No tienes cuenta? <Link to="/register" className="text-primary hover:text-accent font-medium transition-colors">Regístrate</Link>
        </p>
      </div>
    </div>
  );
}
