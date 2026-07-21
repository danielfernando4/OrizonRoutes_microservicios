import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../api/axiosConfig';
import { Calendar, Users, ArrowRight, Loader2, Map, AlertCircle, SearchX } from 'lucide-react';

export default function MyTripsPage() {
  const navigate = useNavigate();
  const [trips, setTrips] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchTrips = async () => {
      try {
        const response = await api.get('/api/catalog/trips/mine');
        setTrips(response.data);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Error al cargar tus viajes');
      } finally {
        setLoading(false);
      }
    };
    fetchTrips();
  }, []);

  const formatDate = (dateString: string) => {
    const d = new Date(dateString);
    return new Intl.DateTimeFormat('es-ES', {
      weekday: 'long', day: 'numeric', month: 'long', hour: '2-digit', minute: '2-digit'
    }).format(d);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen pt-24 px-4 bg-background flex items-center justify-center">
        <div className="glass-panel p-8 rounded-2xl max-w-md w-full text-center">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-foreground mb-2">Error</h2>
          <p className="text-foreground/70 mb-6">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="bg-primary hover:bg-secondary text-white font-medium py-2 px-6 rounded-lg transition-colors cursor-pointer"
          >
            Intentar de nuevo
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen pt-24 pb-12 px-4 bg-background">
      <div className="max-w-4xl mx-auto space-y-8">
        <div className="flex items-center gap-3">
          <Map className="w-7 h-7 text-primary" />
          <h1 className="text-2xl font-bold text-foreground">Mis Viajes Publicados</h1>
        </div>

        {trips.length === 0 ? (
          <div className="glass-panel rounded-2xl p-12 text-center">
            <SearchX className="w-12 h-12 text-foreground/30 mx-auto mb-4" />
            <p className="text-lg font-medium text-foreground/70">
              No has publicado ningún viaje aún
            </p>
            <p className="text-sm text-foreground/50 mt-1">
              Publica tu primer viaje para empezar a compartir rutas
            </p>
            <button
              onClick={() => navigate('/publish')}
              className="mt-6 bg-primary hover:bg-secondary text-white font-medium py-2 px-6 rounded-lg transition-colors cursor-pointer"
            >
              Publicar Viaje
            </button>
          </div>
        ) : (
          <div className="grid gap-4">
            {trips.map(trip => (
              <div
                key={trip.id}
                onClick={() => navigate(`/trips/${trip.id}`)}
                className="glass-panel p-6 cursor-pointer hover:border-primary/50 transition-all group flex flex-col md:flex-row md:items-center justify-between gap-6"
              >
                <div className="flex-1 space-y-4">
                  <div className="flex items-center gap-4 text-lg font-semibold text-foreground">
                    <span>{trip.origin}</span>
                    <ArrowRight className="w-5 h-5 text-primary" />
                    <span>{trip.destination}</span>
                  </div>

                  <div className="flex flex-wrap gap-4 text-sm text-foreground/70">
                    <div className="flex items-center gap-2">
                      <Calendar className="w-4 h-4" />
                      <span className="capitalize">{formatDate(trip.departure_time)}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Users className="w-4 h-4" />
                      <span>{trip.available_seats} de {trip.total_seats} asientos disp.</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-3 md:flex-col md:items-end border-t md:border-t-0 md:border-l border-border/50 pt-4 md:pt-0 md:pl-6">
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                    trip.status === 'active' ? 'bg-green-500/10 text-green-500' : 'bg-red-500/10 text-red-500'
                  }`}>
                    {trip.status === 'active' ? 'Activo' : 'Cerrado'}
                  </span>
                  <div className="text-lg font-bold text-primary">
                    ${trip.price_per_seat.toFixed(2)}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}