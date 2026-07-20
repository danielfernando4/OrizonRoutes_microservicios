import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import api from '../../api/axiosConfig';
import { Search, MapPin, Calendar, Users, ArrowRight, Loader2 } from 'lucide-react';

export default function SearchPage() {
  const navigate = useNavigate();
  const [trips, setTrips] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searching, setSearching] = useState(false);
  const [origin, setOrigin] = useState('');
  const [destination, setDestination] = useState('');

  useEffect(() => {
    fetchTrips();
  }, []);

  const fetchTrips = async (searchOrigin = '', searchDest = '') => {
    setSearching(true);
    try {
      let url = '/api/catalog/trips/';
      const params = new URLSearchParams();
      if (searchOrigin) params.append('origin', searchOrigin);
      if (searchDest) params.append('destination', searchDest);
      if (params.toString()) url += `?${params.toString()}`;

      const response = await api.get(url);
      setTrips(response.data);
    } catch (error) {
      toast.error('Error al buscar viajes');
    } finally {
      setLoading(false);
      setSearching(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchTrips(origin, destination);
  };

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

  return (
    <div className="min-h-screen pt-24 pb-12 px-4 bg-background">
      <div className="max-w-5xl mx-auto space-y-8">
        
        {/* Search Header */}
        <div className="glass-panel p-8 text-center space-y-6">
          <h1 className="text-3xl font-bold text-foreground">¿A dónde quieres ir?</h1>
          <form onSubmit={handleSearch} className="flex flex-col md:flex-row gap-4 max-w-3xl mx-auto">
            <div className="flex-1 relative">
              <MapPin className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-foreground/50" />
              <input
                type="text"
                value={origin}
                onChange={(e) => setOrigin(e.target.value)}
                placeholder="Origen (Ej. Quito)"
                className="w-full pl-12 pr-4 py-4 bg-background/50 border border-border rounded-xl text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all text-lg"
              />
            </div>
            <div className="flex-1 relative">
              <MapPin className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-foreground/50" />
              <input
                type="text"
                value={destination}
                onChange={(e) => setDestination(e.target.value)}
                placeholder="Destino (Ej. Guayaquil)"
                className="w-full pl-12 pr-4 py-4 bg-background/50 border border-border rounded-xl text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all text-lg"
              />
            </div>
            <button
              type="submit"
              disabled={searching}
              className="py-4 px-8 bg-primary text-white rounded-xl font-medium hover:bg-primary/90 transition-all disabled:opacity-50 flex items-center justify-center gap-2 text-lg"
            >
              {searching ? <Loader2 className="w-6 h-6 animate-spin" /> : <Search className="w-6 h-6" />}
              Buscar
            </button>
          </form>
        </div>

        {/* Results */}
        <div className="space-y-4">
          <h2 className="text-xl font-semibold text-foreground">
            {trips.length} {trips.length === 1 ? 'viaje encontrado' : 'viajes encontrados'}
          </h2>
          
          {trips.length === 0 ? (
            <div className="glass-panel p-12 text-center text-foreground/60 border-dashed">
              No hay viajes disponibles para esa ruta en este momento.
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
                        <span>{trip.available_seats} asientos disp.</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between md:flex-col md:items-end gap-2 border-t md:border-t-0 md:border-l border-border/50 pt-4 md:pt-0 md:pl-6">
                    <div className="text-2xl font-bold text-primary">
                      ${trip.price_per_seat.toFixed(2)}
                    </div>
                    <span className="text-sm text-foreground/60">por pasajero</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
