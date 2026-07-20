import { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import api from '../../api/axiosConfig';
import { Car, Plus, Loader2 } from 'lucide-react';

interface Vehicle {
  id: string;
  brand: string;
  model: string;
  capacity: int;
}

export default function MyVehiclesPage() {
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [formData, setFormData] = useState({ brand: '', model: '', capacity: 1 });

  useEffect(() => {
    fetchVehicles();
  }, []);

  const fetchVehicles = async () => {
    try {
      const response = await api.get('/api/catalog/vehicles');
      setVehicles(response.data);
    } catch (error) {
      toast.error('Error al cargar vehículos');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (formData.capacity < 1) {
      toast.error('La capacidad debe ser al menos 1');
      return;
    }
    
    setSubmitting(true);
    try {
      await api.post('/api/catalog/vehicles', formData);
      toast.success('Vehículo registrado exitosamente');
      setFormData({ brand: '', model: '', capacity: 1 });
      fetchVehicles();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Error al registrar vehículo');
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
      <div className="max-w-4xl mx-auto space-y-8">
        <div>
          <h1 className="text-3xl font-bold text-foreground flex items-center gap-2">
            <Car className="w-8 h-8 text-primary" />
            Mis Vehículos
          </h1>
          <p className="text-foreground/70 mt-2">Gestiona los vehículos que usas para conducir en Orizon Routes.</p>
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          <div className="glass-panel p-6">
            <h2 className="text-xl font-semibold text-foreground mb-4 flex items-center gap-2">
              <Plus className="w-5 h-5 text-primary" />
              Registrar Nuevo
            </h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-foreground/80 mb-1">Marca</label>
                <input
                  type="text"
                  required
                  value={formData.brand}
                  onChange={(e) => setFormData({ ...formData, brand: e.target.value })}
                  className="w-full px-4 py-2 bg-background/50 border border-border rounded-xl text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all"
                  placeholder="Ej. Toyota"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-foreground/80 mb-1">Modelo</label>
                <input
                  type="text"
                  required
                  value={formData.model}
                  onChange={(e) => setFormData({ ...formData, model: e.target.value })}
                  className="w-full px-4 py-2 bg-background/50 border border-border rounded-xl text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all"
                  placeholder="Ej. Corolla"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-foreground/80 mb-1">Capacidad (Asientos)</label>
                <input
                  type="number"
                  required
                  min="1"
                  value={formData.capacity}
                  onChange={(e) => setFormData({ ...formData, capacity: parseInt(e.target.value) })}
                  className="w-full px-4 py-2 bg-background/50 border border-border rounded-xl text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all"
                />
              </div>
              <button
                type="submit"
                disabled={submitting}
                className="w-full py-3 px-4 bg-primary text-white rounded-xl font-medium hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 focus:ring-offset-background transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {submitting ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Registrar Vehículo'}
              </button>
            </form>
          </div>

          <div className="space-y-4">
            <h2 className="text-xl font-semibold text-foreground mb-4">Vehículos Registrados</h2>
            {vehicles.length === 0 ? (
              <div className="glass-panel p-8 text-center text-foreground/60 border-dashed">
                No tienes vehículos registrados aún.
              </div>
            ) : (
              vehicles.map((v) => (
                <div key={v.id} className="glass-panel p-4 flex items-center justify-between hover:border-primary/50 transition-all">
                  <div>
                    <h3 className="font-semibold text-foreground">{v.brand} {v.model}</h3>
                    <p className="text-sm text-foreground/70">{v.capacity} asientos disponibles</p>
                  </div>
                  <Car className="w-6 h-6 text-primary/50" />
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
