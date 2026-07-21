import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../api/axiosConfig';
import { useAuth } from '../../context/AuthContext';
import { MessageCircle, Loader2, AlertCircle, SearchX, ChevronLeft } from 'lucide-react';
import ChatWindows from './ChatWindows';

interface Room {
  _id: string;
  trip_id: string;
  passenger_id: string;
  created_at: string;
}

interface TripInfo {
  id: string;
  origin: string;
  destination: string;
  departure_time: string;
}

export default function GlobalChatPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [rooms, setRooms] = useState<Room[]>([]);
  const [tripsMap, setTripsMap] = useState<Record<string, TripInfo>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedRoom, setSelectedRoom] = useState<Room | null>(null);

  useEffect(() => {
    if (!user) {
      setLoading(false);
      return;
    }
    const fetchData = async () => {
      try {
        let roomsData: Room[];

        if (user.role === 'conductor') {
          const tripsRes = await api.get('/api/catalog/trips/mine');
          const trips: TripInfo[] = tripsRes.data;
          const map: Record<string, TripInfo> = {};
          trips.forEach((t) => { map[t.id] = t; });
          setTripsMap(map);

          if (trips.length === 0) {
            setRooms([]);
            setLoading(false);
            return;
          }

          const tripIds = trips.map((t) => t.id).join(',');
          const roomsRes = await api.get('/api/chat/rooms', { params: { trip_ids: tripIds } });
          roomsData = roomsRes.data;
        } else {
          const roomsRes = await api.get('/api/chat/rooms');
          roomsData = roomsRes.data;

          const uniqueTripIds = [...new Set(roomsData.map((r) => r.trip_id))];
          const map: Record<string, TripInfo> = {};
          await Promise.all(uniqueTripIds.map(async (tid) => {
            try {
              const res = await api.get(`/api/catalog/trips/${tid}`);
              map[tid] = res.data;
            } catch { /* skip */ }
          }));
          setTripsMap(map);
        }

        const uniqueRooms = roomsData.filter(
          (room, index, self) =>
            index === self.findIndex((r) => r.trip_id === room.trip_id && r.passenger_id === room.passenger_id)
        );
        setRooms(uniqueRooms);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Error al cargar conversaciones');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [user]);

  const formatDate = (iso: string) => {
    const d = new Date(iso);
    return d.toLocaleDateString('es-ES', { day: 'numeric', month: 'short' });
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
          <button onClick={() => window.location.reload()} className="bg-primary hover:bg-secondary text-white font-medium py-2 px-6 rounded-lg transition-colors cursor-pointer">
            Intentar de nuevo
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen pt-24 pb-12 px-4 bg-background">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center gap-3 mb-8">
          <MessageCircle className="w-7 h-7 text-primary" />
          <h1 className="text-2xl font-bold text-foreground">Mis Conversaciones</h1>
        </div>

        {rooms.length === 0 ? (
          <div className="glass-panel rounded-2xl p-12 text-center">
            <SearchX className="w-12 h-12 text-foreground/30 mx-auto mb-4" />
            <p className="text-lg font-medium text-foreground/70">No tienes conversaciones activas</p>
            <p className="text-sm text-foreground/50 mt-1">
              {user?.role === 'conductor'
                ? 'Los pasajeros te enviarán mensaje cuando reserven un viaje contigo.'
                : 'Reserva un viaje y contacta al conductor para coordinar.'}
            </p>
            <button
              onClick={() => navigate('/')}
              className="mt-6 bg-primary hover:bg-secondary text-white font-medium py-2 px-6 rounded-lg transition-colors cursor-pointer"
            >
              Explorar viajes
            </button>
          </div>
        ) : (
          <div className="grid lg:grid-cols-3 gap-6">
            {/* Left: Conversation List */}
            <div className="lg:col-span-1 space-y-2 max-h-[70vh] overflow-y-auto pr-2">
              {rooms.map((room) => {
                const trip = tripsMap[room.trip_id];
                const isSelected = selectedRoom?._id === room._id;
                return (
                  <button
                    key={room._id}
                    onClick={() => setSelectedRoom(room)}
                    className={`w-full text-left glass-panel p-4 rounded-xl transition-all cursor-pointer ${
                      isSelected ? 'border-primary/70 ring-1 ring-primary/30' : 'hover:border-primary/30'
                    }`}
                  >
                    <div className="flex items-center gap-2 text-sm font-semibold text-foreground mb-1">
                      {trip ? (
                        <span className="truncate">{trip.origin} → {trip.destination}</span>
                      ) : (
                        <span className="text-foreground/50">Viaje {room.trip_id.substring(0, 8)}</span>
                      )}
                    </div>
                    <div className="flex items-center justify-between text-xs text-foreground/50">
                      <span>
                        {user?.role === 'conductor'
                          ? `Pasajero ${room.passenger_id.substring(0, 6)}`
                          : 'Conductor'}
                      </span>
                      {trip && <span>{formatDate(trip.departure_time)}</span>}
                    </div>
                  </button>
                );
              })}
            </div>

            {/* Right: Chat Window */}
            <div className="lg:col-span-2">
              {selectedRoom ? (
                <div>
                  <div className="flex items-center gap-2 mb-4 lg:hidden">
                    <button onClick={() => setSelectedRoom(null)} className="text-primary hover:underline text-sm cursor-pointer">
                      <ChevronLeft className="w-4 h-4 inline" /> Volver
                    </button>
                  </div>
                  <ChatWindows
                    tripId={selectedRoom.trip_id}
                    passengerId={selectedRoom.passenger_id}
                    otherPartyName={
                      user?.role === 'conductor'
                        ? `Pasajero ${selectedRoom.passenger_id.substring(0, 6)}`
                        : (tripsMap[selectedRoom.trip_id]
                          ? `${tripsMap[selectedRoom.trip_id].origin} → ${tripsMap[selectedRoom.trip_id].destination}`
                          : 'Conductor')
                    }
                  />
                </div>
              ) : (
                <div className="glass-panel rounded-2xl h-[32rem] flex items-center justify-center text-foreground/40">
                  <div className="text-center">
                    <MessageCircle className="w-12 h-12 mx-auto mb-3 opacity-40" />
                    <p className="font-medium">Selecciona una conversación</p>
                    <p className="text-sm mt-1">Elige un chat del panel izquierdo para empezar</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}