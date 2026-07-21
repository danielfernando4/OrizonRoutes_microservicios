import { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import api from '../../api/axiosConfig';
import { Car, Plus, Loader2, Pencil, Trash2, X, Check } from 'lucide-react';

interface Vehicle {
  id: string;
  brand: string;
  model: string;
  capacity: number;
}

export default function MyVehiclesPage() {
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [formData, setFormData] = useState({ brand: '', model: '', capacity: 1 });
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editData, setEditData] = useState({ brand: '', model: '', capacity: 1 });
  const [savingEdit, setSavingEdit] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);

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

  const startEdit = (v: Vehicle) => {
    setEditingId(v.id);
    setEditData({ brand: v.brand, model: v.model, capacity: v.capacity });
  };

  const cancelEdit = () => {
    setEditingId(null);
  };

  const saveEdit = async (id: string) => {
    if (!editData.brand.trim() || !editData.model.trim()) {
      toast.error('Marca y modelo son requeridos');
      return;
    }
    if (editData.capacity < 1) {
      toast.error('La capacidad debe ser al menos 1');
      return;
    }
    setSavingEdit(true);
    try {
      const payload: Record<string, string | number> = {};
      if (editData.brand !== vehicles.find(v => v.id === id)?.brand) payload.brand = editData.brand;
      if (editData.model !== vehicles.find(v => v.id === id)?.model) payload.model = editData.model;
      if (editData.capacity !== vehicles.find(v => v.id === id)?.capacity) payload.capacity = editData.capacity;
      if (Object.keys(payload).length === 0) {
        setEditingId(null);
        return;
      }
      await api.put(`/api/catalog/vehicles/${id}`, payload);
      toast.success('Vehículo actualizado');
      setEditingId(null);
      fetchVehicles();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Error al actualizar vehículo');
    } finally {
      setSavingEdit(false);
    }
  };

  const confirmDelete = async (id: string) => {
    setDeletingId(id);
    try {
      await api.delete(`/api/catalog/vehicles/${id}`);
      toast.success('Vehículo eliminado');
      fetchVehicles();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Error al eliminar vehículo');
    } finally {
      setDeletingId(null);
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
                  {editingId === v.id ? (
                    <div className="flex-1 space-y-2">
                      <input
                        type="text"
                        value={editData.brand}
                        onChange={(e) => setEditData({ ...editData, brand: e.target.value })}
                        className="w-full px-3 py-1.5 bg-background/50 border border-border rounded-lg text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
                        placeholder="Marca"
                      />
                      <input
                        type="text"
                        value={editData.model}
                        onChange={(e) => setEditData({ ...editData, model: e.target.value })}
                        className="w-full px-3 py-1.5 bg-background/50 border border-border rounded-lg text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
                        placeholder="Modelo"
                      />
                      <input
                        type="number"
                        min="1"
                        value={editData.capacity}
                        onChange={(e) => setEditData({ ...editData, capacity: parseInt(e.target.value) || 1 })}
                        className="w-full px-3 py-1.5 bg-background/50 border border-border rounded-lg text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
                      />
                      <div className="flex gap-2 pt-1">
                        <button
                          onClick={() => saveEdit(v.id)}
                          disabled={savingEdit}
                          className="flex items-center gap-1 px-3 py-1.5 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50"
                        >
                          {savingEdit ? <Loader2 className="w-4 h-4 animate-spin" /> : <Check className="w-4 h-4" />}
                          Guardar
                        </button>
                        <button
                          onClick={cancelEdit}
                          className="flex items-center gap-1 px-3 py-1.5 bg-foreground/20 text-foreground text-sm rounded-lg hover:bg-foreground/30 transition-colors"
                        >
                          <X className="w-4 h-4" />
                          Cancelar
                        </button>
                      </div>
                    </div>
                  ) : (
                    <>
                      <div>
                        <h3 className="font-semibold text-foreground">{v.brand} {v.model}</h3>
                        <p className="text-sm text-foreground/70">{v.capacity} asientos disponibles</p>
                      </div>
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => startEdit(v)}
                          className="p-2 text-foreground/50 hover:text-primary transition-colors"
                          title="Editar"
                        >
                          <Pencil className="w-5 h-5" />
                        </button>
                        <button
                          onClick={() => {
                            if (window.confirm(`¿Eliminar ${v.brand} ${v.model}? También se eliminarán sus viajes asociados.`)) {
                              confirmDelete(v.id);
                            }
                          }}
                          disabled={deletingId === v.id}
                          className="p-2 text-foreground/50 hover:text-red-500 transition-colors disabled:opacity-50"
                          title="Eliminar"
                        >
                          {deletingId === v.id ? <Loader2 className="w-5 h-5 animate-spin" /> : <Trash2 className="w-5 h-5" />}
                        </button>
                      </div>
                    </>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}