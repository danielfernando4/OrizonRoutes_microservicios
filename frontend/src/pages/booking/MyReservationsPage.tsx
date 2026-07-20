import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../api/axiosConfig';
import {
  CalendarClock,
  MapPin,
  Calendar,
  Clock,
  Users,
  CreditCard,
  AlertCircle,
  SearchX,
} from 'lucide-react';

interface Reserva {
  reservation_id: string;
  trip_id: string;
  origin: string;
  destination: string;
  departure_datetime: string;
  seats_reserved: number;
  total_price: number;
  status: string;
  reservation_code: string;
  created_at: string;
}

const statusConfig: Record<string, { label: string; classes: string }> = {
  PAID: { label: 'Pagado', classes: 'bg-green-100 text-green-700' },
  PENDING: { label: 'Pendiente', classes: 'bg-yellow-100 text-yellow-700' },
  CANCELLED: { label: 'Cancelado', classes: 'bg-red-100 text-red-700' },
  REFUNDED: { label: 'Reembolsado', classes: 'bg-purple-100 text-purple-700' },
};

function StatusBadge({ estado }: { estado: string }) {
  const config = statusConfig[estado] || {
    label: estado,
    classes: 'bg-gray-100 text-gray-700',
  };
  return (
    <span
      className={`text-xs px-3 py-1 rounded-full font-semibold ${config.classes}`}
    >
      {config.label}
    </span>
  );
}

function SkeletonCard() {
  return (
    <div className="glass-panel rounded-2xl p-6 animate-pulse space-y-4">
      <div className="h-5 bg-white/40 rounded w-2/3" />
      <div className="h-4 bg-white/40 rounded w-1/2" />
      <div className="flex gap-4">
        <div className="h-4 bg-white/40 rounded w-1/4" />
        <div className="h-4 bg-white/40 rounded w-1/4" />
      </div>
      <div className="h-4 bg-white/40 rounded w-1/3" />
    </div>
  );
}

export default function MyReservationsPage() {
  const [reservas, setReservas] = useState<Reserva[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const fetchReservas = async () => {
      try {
        const response = await api.get('/api/booking/my-reservations');
        setReservas(response.data.items || []);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Error al cargar las reservas');
      } finally {
        setLoading(false);
      }
    };
    fetchReservas();
  }, []);

  const formatDate = (iso: string) => {
    const date = new Date(iso);
    return date.toLocaleDateString('es-ES', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
    });
  };

  const formatTime = (iso: string) => {
    const date = new Date(iso);
    return date.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' });
  };

  const formatShortDate = (iso: string) => {
    const date = new Date(iso);
    return date.toLocaleDateString('es-ES', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen pt-24 px-4 bg-background">
        <div className="max-w-3xl mx-auto space-y-4">
          <div className="h-8 bg-white/40 rounded w-48 animate-pulse mb-6" />
          <SkeletonCard />
          <SkeletonCard />
        </div>
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
    <div className="min-h-screen pt-24 px-4 bg-background">
      <div className="max-w-3xl mx-auto pb-12">
        <div className="flex items-center gap-3 mb-8">
          <CalendarClock className="w-7 h-7 text-primary" />
          <h1 className="text-2xl font-bold text-foreground">Mis Reservas</h1>
        </div>

        {reservas.length === 0 ? (
          <div className="glass-panel rounded-2xl p-12 text-center">
            <SearchX className="w-12 h-12 text-foreground/30 mx-auto mb-4" />
            <p className="text-lg font-medium text-foreground/70">
              No tienes reservas aún
            </p>
            <p className="text-sm text-foreground/50 mt-1">
              Explora viajes y reserva tu primera aventura
            </p>
            <button
              onClick={() => navigate('/')}
              className="mt-6 bg-primary hover:bg-secondary text-white font-medium py-2 px-6 rounded-lg transition-colors cursor-pointer"
            >
              Explorar viajes
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            {reservas.map((reserva) => (
              <div
                key={reserva.reservation_id}
                className="glass-panel rounded-2xl p-6 hover:shadow-lg transition-shadow"
              >
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <p className="text-xs text-foreground/50 mb-1">
                      {formatShortDate(reserva.created_at)}
                    </p>
                    <h3 className="font-bold text-foreground flex items-center gap-2">
                      <MapPin className="w-4 h-4 text-primary flex-shrink-0" />
                      {reserva.origin} → {reserva.destination}
                    </h3>
                  </div>
                  <StatusBadge estado={reserva.status} />
                </div>

                <div className="flex flex-wrap gap-x-6 gap-y-2 text-sm text-foreground/70">
                  <div className="flex items-center gap-1.5">
                    <Calendar className="w-4 h-4 text-primary" />
                    {formatDate(reserva.departure_datetime)}
                  </div>
                  <div className="flex items-center gap-1.5">
                    <Clock className="w-4 h-4 text-primary" />
                    {formatTime(reserva.departure_datetime)}
                  </div>
                  <div className="flex items-center gap-1.5">
                    <Users className="w-4 h-4 text-primary" />
                    {reserva.seats_reserved} asiento{reserva.seats_reserved !== 1 ? 's' : ''}
                  </div>
                  <div className="flex items-center gap-1.5">
                    <CreditCard className="w-4 h-4 text-primary" />
                    ${Number(reserva.total_price).toFixed(2)}
                  </div>
                </div>

                {reserva.reservation_code && (
                  <div className="mt-3 pt-3 border-t border-white/40">
                    <span className="text-xs text-foreground/50">
                      Código: {''}
                    </span>
                    <span className="text-sm font-mono font-bold text-primary">
                      {reserva.reservation_code}
                    </span>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
