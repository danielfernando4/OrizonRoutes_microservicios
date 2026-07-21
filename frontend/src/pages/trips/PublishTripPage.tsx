import { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import { useNavigate } from 'react-router-dom';
import api from '../../api/axiosConfig';
import { MapPin, Calendar, DollarSign, Send, Loader2 } from 'lucide-react';

export default function PublishTripPage() {
  const navigate = useNavigate();
  const [vehicles, setVehicles] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    vehicle_id: '',
    origin: '',
    destination: '',
    departure_time: '',
    price_per_seat: 10
  });

  useEffect(() => {
    fetchVehicles();
  }, []);

  const fetchVehicles = async () => {
    try {
      const response = await api.get('/api/catalog/vehicles');
      setVehicles(response.data);
      if (response.data.length > 0) {
        setFormData(prev => ({ ...prev, vehicle_id: response.data[0].id }));
      }
    } catch (error) {
      toast.error('Error al cargar tus vehículos');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.vehicle_id) {
      toast.error('Debes registrar un vehículo primero');
      return;
    }
    
    setSubmitting(true);
    try {
      // Parsear la fecha a formato ISO 8601
      const payload = {
        ...formData,
        departure_time: new Date(formData.departure_time).toISOString()
      };
      const response = await api.post('/api/catalog/trips', payload);
      toast.success('¡Viaje publicado exitosamente!');
      navigate(`/trips/${response.data.id}`);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Error al publicar el viaje');
    } finally {
      setSubmitting(false);
    }
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
      <div className="max-w-2xl mx-auto space-y-8">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Publicar un Viaje</h1>
          <p className="text-foreground/70 mt-2">Comparte tu ruta y ayuda a otros pasajeros a llegar a su destino.</p>
        </div>

        {vehicles.length === 0 ? (
          <div className="glass-panel p-8 text-center">
            <h2 className="text-xl font-semibold mb-4 text-foreground">No tienes vehículos registrados</h2>
            <p className="text-foreground/70 mb-6">Para publicar un viaje, primero necesitas registrar el vehículo que vas a conducir.</p>
            <button 
              onClick={() => navigate('/vehicles')}
              className="px-6 py-3 bg-primary text-white rounded-xl font-medium hover:bg-primary/90 transition-all"
            >
              Registrar Vehículo
            </button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="glass-panel p-8 space-y-6">
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-foreground/80 mb-1 flex items-center gap-2">
                  <MapPin className="w-4 h-4 text-primary" /> Origen
                </label>
                <input
                  type="text"
                  required
                  value={formData.origin}
                  onChange={(e) => setFormData({ ...formData, origin: e.target.value })}
                  className="w-full px-4 py-3 bg-background/50 border border-border rounded-xl text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all"
                  placeholder="Ciudad o lugar de salida"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-foreground/80 mb-1 flex items-center gap-2">
                  <MapPin className="w-4 h-4 text-primary" /> Destino
                </label>
                <input
                  type="text"
                  required
                  value={formData.destination}
                  onChange={(e) => setFormData({ ...formData, destination: e.target.value })}
                  className="w-full px-4 py-3 bg-background/50 border border-border rounded-xl text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all"
                  placeholder="Ciudad o lugar de llegada"
                />
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-foreground/80 mb-1 flex items-center gap-2">
                  <Calendar className="w-4 h-4 text-primary" /> Fecha y Hora
                </label>
                <input
                  type="datetime-local"
                  required
                  value={formData.departure_time}
                  onChange={(e) => setFormData({ ...formData, departure_time: e.target.value })}
                  className="w-full px-4 py-3 bg-background/50 border border-border rounded-xl text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-foreground/80 mb-1 flex items-center gap-2">
                  <DollarSign className="w-4 h-4 text-primary" /> Precio por Asiento
                </label>
                <input
                  type="number"
                  step="0.01"
                  required
                  min="0.1"
                  value={formData.price_per_seat}
                  onChange={(e) => setFormData({ ...formData, price_per_seat: parseFloat(e.target.value) })}
                  className="w-full px-4 py-3 bg-background/50 border border-border rounded-xl text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-foreground/80 mb-1">Vehículo a utilizar</label>
              <select
                required
                value={formData.vehicle_id}
                onChange={(e) => setFormData({ ...formData, vehicle_id: e.target.value })}
                className="w-full px-4 py-3 bg-background/50 border border-border rounded-xl text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all"
              >
                {vehicles.map(v => (
                  <option key={v.id} value={v.id}>
                    {v.brand} {v.model} ({v.capacity} asientos)
                  </option>
                ))}
              </select>
            </div>

            <button
              type="submit"
              disabled={submitting}
              className="w-full py-4 bg-primary text-white rounded-xl font-medium hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 focus:ring-offset-background transition-all disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {submitting ? <Loader2 className="w-6 h-6 animate-spin" /> : <><Send className="w-5 h-5" /> Publicar Viaje</>}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
