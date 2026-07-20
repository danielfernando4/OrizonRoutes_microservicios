import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import api from '../../api/axiosConfig';
import { Calendar, DollarSign, Users, ArrowRight, Loader2, Navigation, MessageCircle } from 'lucide-react';
import CheckoutWidget from '../booking/CheckoutWidget';
import ChatWindows from '../chat/ChatWindows';
import { useAuth } from '../../context/AuthContext';

export default function TripDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [trip, setTrip] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [showChat, setShowChat] = useState(false);
  const { user } = useAuth();
  const [driverRooms, setDriverRooms] = useState<any[]>([]);
  const [selectedPassengerId, setSelectedPassengerId] = useState<string | null>(null);

  useEffect(() => {
    const fetchTrip = async () => {
      try {
        const response = await api.get(`/api/catalog/trips/${id}`);
        setTrip(response.data);
      } catch (error) {
        toast.error('Viaje no encontrado');
        navigate('/');
      } finally {
        setLoading(false);
      }
    };
    fetchTrip();
  }, [id, navigate]);

  useEffect(() => {
    if (showChat && trip && user?.id === trip.driver_id) {
      api.get(`/api/chat/rooms/${trip.id}`)
        .then(res => setDriverRooms(res.data))
        .catch(console.error);
    }
  }, [showChat, trip, user?.id]);

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

  if (!trip) return null;

  return (
    <div className="min-h-screen pt-24 pb-12 px-4 bg-background">
      <div className="max-w-6xl mx-auto grid lg:grid-cols-3 gap-8">
        
        {/* Left Column: Trip Details */}
        <div className="lg:col-span-2 space-y-6">
          <div className="glass-panel p-8">
            <div className="flex items-center justify-between mb-8">
              <h1 className="text-3xl font-bold text-foreground">Detalle del Viaje</h1>
              <span className={`px-4 py-1 rounded-full text-sm font-medium ${trip.status === 'active' ? 'bg-green-500/10 text-green-500' : 'bg-red-500/10 text-red-500'}`}>
                {trip.status === 'active' ? 'Activo' : 'Cerrado'}
              </span>
            </div>

            <div className="flex items-center gap-6 text-2xl font-semibold text-foreground mb-12">
              <div className="flex-1 text-center bg-background/50 p-6 rounded-2xl border border-border">
                {trip.origin}
              </div>
              <ArrowRight className="w-8 h-8 text-primary shrink-0" />
              <div className="flex-1 text-center bg-background/50 p-6 rounded-2xl border border-border">
                {trip.destination}
              </div>
            </div>

            <div className="grid sm:grid-cols-2 gap-6">
              <div className="flex items-center gap-4 bg-background/30 p-4 rounded-xl border border-border/50">
                <div className="p-3 bg-primary/10 rounded-lg text-primary">
                  <Calendar className="w-6 h-6" />
                </div>
                <div>
                  <p className="text-sm text-foreground/60">Salida</p>
                  <p className="font-medium text-foreground capitalize">{formatDate(trip.departure_time)}</p>
                </div>
              </div>
              
              <div className="flex items-center gap-4 bg-background/30 p-4 rounded-xl border border-border/50">
                <div className="p-3 bg-primary/10 rounded-lg text-primary">
                  <Navigation className="w-6 h-6" />
                </div>
                <div>
                  <p className="text-sm text-foreground/60">Ruta OSRM</p>
                  <p className="font-medium text-foreground">{trip.distance_km} km ({trip.duration_min} min)</p>
                </div>
              </div>

              <div className="flex items-center gap-4 bg-background/30 p-4 rounded-xl border border-border/50">
                <div className="p-3 bg-primary/10 rounded-lg text-primary">
                  <Users className="w-6 h-6" />
                </div>
                <div>
                  <p className="text-sm text-foreground/60">Asientos</p>
                  <p className="font-medium text-foreground">{trip.available_seats} de {trip.total_seats} disponibles</p>
                </div>
              </div>

              <div className="flex items-center gap-4 bg-background/30 p-4 rounded-xl border border-border/50">
                <div className="p-3 bg-primary/10 rounded-lg text-primary">
                  <DollarSign className="w-6 h-6" />
                </div>
                <div>
                  <p className="text-sm text-foreground/60">Precio unitario</p>
                  <p className="font-medium text-foreground">${trip.price_per_seat.toFixed(2)}</p>
                </div>
              </div>
            </div>

            {/* Chat integration toggle */}
            <div className="mt-8 pt-8 border-t border-border">
              <button 
                onClick={() => {
                  setShowChat(!showChat);
                  setSelectedPassengerId(null);
                }}
                className="w-full flex items-center justify-center gap-2 py-4 bg-background/80 hover:bg-background border border-border rounded-xl text-foreground font-medium transition-all"
              >
                <MessageCircle className="w-5 h-5 text-primary" />
                {showChat ? 'Ocultar Chat de este Viaje' : 'Abrir Chat de este Viaje'}
              </button>
            </div>
            
            {showChat && (
              <div className="mt-4 rounded-xl overflow-hidden border border-border">
                {user?.id === trip.driver_id ? (
                  /* Vista de Conductor */
                  <div className="flex flex-col h-[500px]">
                    {!selectedPassengerId ? (
                      <div className="p-6 bg-background/80 flex-1 overflow-y-auto">
                        <h3 className="text-lg font-bold mb-4 text-foreground">Bandeja de Mensajes</h3>
                        {driverRooms.length === 0 ? (
                          <p className="text-foreground/60 text-sm">Nadie ha enviado mensajes aún.</p>
                        ) : (
                          <div className="space-y-3">
                            {driverRooms.map((room) => (
                              <button
                                key={room._id}
                                onClick={() => setSelectedPassengerId(room.passenger_id)}
                                className="w-full text-left p-4 rounded-xl border border-border/50 hover:border-primary/50 transition-colors bg-white/5"
                              >
                                <span className="font-medium text-foreground">Chat con pasajero: {room.passenger_id}</span>
                                <span className="block text-xs text-foreground/40 mt-1">Sala creada: {new Date(room.created_at).toLocaleDateString()}</span>
                              </button>
                            ))}
                          </div>
                        )}
                      </div>
                    ) : (
                      <div className="flex flex-col h-full">
                        <div className="p-2 border-b border-border bg-background flex items-center">
                           <button onClick={() => setSelectedPassengerId(null)} className="text-sm text-primary hover:underline px-2">
                             &larr; Volver a la lista
                           </button>
                        </div>
                        <ChatWindows tripId={String(trip.id)} passengerId={selectedPassengerId} otherPartyName={`Pasajero ${selectedPassengerId.substring(0,6)}`} />
                      </div>
                    )}
                  </div>
                ) : (
                  /* Vista de Pasajero */
                  <div className="h-[500px]">
                    <ChatWindows tripId={String(trip.id)} passengerId={String(user?.id)} otherPartyName="Conductor" />
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Checkout Widget (Booking Service) */}
        <div className="lg:col-span-1">
          <div className="sticky top-24">
            <CheckoutWidget
              tripId={String(trip.id)}
              origin={trip.origin}
              destination={trip.destination}
              departureTime={trip.departure_time}
              pricePerSeat={trip.price_per_seat}
              availableSeats={trip.available_seats}
            />
          </div>
        </div>

      </div>
    </div>
  );
}
