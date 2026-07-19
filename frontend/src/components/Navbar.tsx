import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { LogOut, User as UserIcon, Map, LogIn, CalendarClock } from 'lucide-react';

export default function Navbar() {
  const { user, logout } = useAuth();

  return (
    <nav className="fixed w-full z-50 top-0 transition-all duration-300 glass-panel border-b-0 rounded-b-2xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <Link to="/" className="flex items-center space-x-2">
              <div className="bg-primary p-2 rounded-lg">
                <Map className="w-6 h-6 text-white" />
              </div>
              <span className="text-xl font-bold text-foreground tracking-tight">
                Orizon Routes
              </span>
            </Link>
          </div>
          
          <div className="flex items-center space-x-4">
            {user ? (
              <>
                <Link
                  to="/my-reservations"
                  className="flex items-center space-x-1.5 text-foreground/70 hover:text-primary transition-colors text-sm font-medium"
                  title="Mis Reservas"
                >
                  <CalendarClock className="w-4 h-4" />
                  <span className="hidden sm:inline">Mis Reservas</span>
                </Link>
                <div className="flex items-center space-x-2 px-3 py-1.5 rounded-full bg-white/50 border border-white/40">
                  <UserIcon className="w-4 h-4 text-primary" />
                  <span className="text-sm font-medium text-foreground">{user.name}</span>
                  <span className="text-xs px-2 py-0.5 rounded-full bg-primary/10 text-primary font-semibold">
                    {user.role}
                  </span>
                </div>
                <button
                  onClick={logout}
                  className="flex items-center space-x-2 text-foreground/70 hover:text-accent transition-colors cursor-pointer"
                  title="Cerrar sesión"
                >
                  <LogOut className="w-5 h-5" />
                </button>
              </>
            ) : (
              <Link 
                to="/login"
                className="flex items-center space-x-2 bg-primary hover:bg-secondary text-white px-4 py-2 rounded-lg transition-colors cursor-pointer shadow-md shadow-primary/20 font-medium"
              >
                <LogIn className="w-4 h-4" />
                <span>Iniciar Sesión</span>
              </Link>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
