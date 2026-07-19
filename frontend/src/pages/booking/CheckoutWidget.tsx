import { useState } from 'react';
import api from '../../api/axiosConfig';
import { CreditCard, Minus, Plus, MapPin, Calendar, Clock } from 'lucide-react';
import { toast } from 'react-toastify';

interface CheckoutWidgetProps {
  tripId: string;
  origin: string;
  destination: string;
  departureTime: string;
  pricePerSeat: number;
  availableSeats: number;
}

export default function CheckoutWidget({
  tripId,
  origin,
  destination,
  departureTime,
  pricePerSeat,
  availableSeats,
}: CheckoutWidgetProps) {
  const [seats, setSeats] = useState(1);
  const [loading, setLoading] = useState(false);

  const total = seats * pricePerSeat;

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

  const handleReserve = async () => {
    setLoading(true);
    try {
      const response = await api.post('/booking/reserve', {
        trip_id: tripId,
        seats,
      });
      const { approval_url } = response.data;
      window.location.href = approval_url;
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Error al procesar la reserva');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-panel rounded-2xl p-6 space-y-5">
      <h3 className="text-lg font-bold text-foreground flex items-center gap-2">
        <CreditCard className="w-5 h-5 text-primary" />
        Reservar Viaje
      </h3>

      <div className="space-y-2 text-sm text-foreground/80">
        <div className="flex items-center gap-2">
          <MapPin className="w-4 h-4 text-primary flex-shrink-0" />
          <span>
            {origin} → {destination}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <Calendar className="w-4 h-4 text-primary flex-shrink-0" />
          <span>{formatDate(departureTime)}</span>
        </div>
        <div className="flex items-center gap-2">
          <Clock className="w-4 h-4 text-primary flex-shrink-0" />
          <span>{formatTime(departureTime)}</span>
        </div>
      </div>

      <div className="border-t border-white/40 pt-4">
        <label className="block text-sm font-medium text-foreground/80 mb-2">
          Número de asientos
        </label>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setSeats(Math.max(1, seats - 1))}
            disabled={seats <= 1}
            className="w-10 h-10 rounded-lg bg-white/50 border border-white/40 flex items-center justify-center hover:bg-primary/10 transition-colors disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
          >
            <Minus className="w-4 h-4 text-foreground" />
          </button>
          <span className="text-2xl font-bold text-foreground w-8 text-center">
            {seats}
          </span>
          <button
            onClick={() => setSeats(Math.min(availableSeats, seats + 1))}
            disabled={seats >= availableSeats}
            className="w-10 h-10 rounded-lg bg-white/50 border border-white/40 flex items-center justify-center hover:bg-primary/10 transition-colors disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
          >
            <Plus className="w-4 h-4 text-foreground" />
          </button>
          <span className="text-sm text-foreground/60 ml-2">
            ({availableSeats} disponibles)
          </span>
        </div>
      </div>

      <div className="border-t border-white/40 pt-4 space-y-1">
        <div className="flex justify-between text-sm text-foreground/70">
          <span>Precio por asiento</span>
          <span>${pricePerSeat.toFixed(2)}</span>
        </div>
        <div className="flex justify-between text-lg font-bold text-foreground">
          <span>Total</span>
          <span>${total.toFixed(2)}</span>
        </div>
      </div>

      <button
        onClick={handleReserve}
        disabled={loading}
        className="w-full bg-primary hover:bg-secondary text-white font-medium py-3 px-4 rounded-lg transition-colors duration-200 shadow-lg shadow-primary/30 disabled:opacity-60 disabled:cursor-not-allowed cursor-pointer flex items-center justify-center gap-2"
      >
        {loading ? (
          <span className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
        ) : (
          <>
            <CreditCard className="w-5 h-5" />
            Reservar con PayPal
          </>
        )}
      </button>
    </div>
  );
}
