import { useState } from 'react';
import { MessageCircle } from 'lucide-react';
import ChatWindow from './ChatWindows';

/**
 * Página temporal SOLO para probar el chat de forma aislada mientras
 * TripDetailPage (Módulo 2) no está lista. En producción, ChatWindow se
 * monta directamente dentro de TripDetailPage con el trip_id real de un
 * viaje existente — esta página y su ruta en App.tsx deberían eliminarse
 * (o dejarse detrás de una bandera de desarrollo) antes de integrar todo.
 */
export default function ChatTestPage() {
  const [tripId, setTripId] = useState('');
  const [passengerId, setPassengerId] = useState('');
  const [activeTripId, setActiveTripId] = useState<string | null>(null);

  return (
    <div className="min-h-screen pt-24 px-4 bg-background">
      <div className="max-w-lg mx-auto space-y-6">
        <div className="flex items-center gap-3">
          <MessageCircle className="w-7 h-7 text-primary" />
          <h1 className="text-2xl font-bold text-foreground">
            Prueba manual del Chat (Módulo 4)
          </h1>
        </div>

        <div className="glass-panel rounded-2xl p-6 space-y-3">
          <label className="text-sm font-medium text-foreground/70">
            Trip ID
          </label>
          <input
            type="text"
            value={tripId}
            onChange={(e) => setTripId(e.target.value)}
            placeholder="uuid-del-viaje"
            className="w-full bg-white/60 border border-white/40 rounded-lg px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/40"
          />
          <label className="text-sm font-medium text-foreground/70">
            Passenger ID
          </label>
          <input
            type="text"
            value={passengerId}
            onChange={(e) => setPassengerId(e.target.value)}
            placeholder="tu-id-de-pasajero"
            className="w-full bg-white/60 border border-white/40 rounded-lg px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/40"
          />
          <button
            onClick={() => setActiveTripId(tripId)}
            disabled={!tripId.trim() || !passengerId.trim()}
            className="w-full bg-primary hover:bg-secondary disabled:opacity-40 text-white font-medium px-4 py-2 rounded-lg transition-colors cursor-pointer"
          >
            Conectar
          </button>
        </div>

        {activeTripId && (
          <ChatWindow tripId={activeTripId} passengerId={passengerId} />
        )}
      </div>
    </div>
  );
}
