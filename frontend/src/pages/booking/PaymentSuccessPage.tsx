import { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import api from '../../api/axiosConfig';
import { CheckCircle, XCircle, Loader2, CalendarClock } from 'lucide-react';
import { toast } from 'react-toastify';

interface PaymentResult {
  reservation_id: string;
  reservation_code: string;
  status: string;
  seats_reserved: number;
  total_price: number;
  trip_id: string;
}

export default function PaymentSuccessPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [result, setResult] = useState<PaymentResult | null>(null);
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    const token = searchParams.get('token');
    const stored = sessionStorage.getItem('paymentResult');

    if (stored) {
      setResult(JSON.parse(stored));
      setStatus('success');
      return;
    }

    if (!token) {
      setStatus('error');
      setErrorMsg('No se recibió información de pago.');
      return;
    }

    let active = true;

    const confirmPayment = async () => {
      try {
        const response = await api.post('/api/booking/confirm-payment', {
          paypal_order_id: token,
        });
        if (!active) return;
        const data = response.data;
        sessionStorage.setItem('paymentResult', JSON.stringify(data));
        setResult(data);
        setStatus('success');
        toast.success('¡Pago confirmado exitosamente!');
      } catch (err: any) {
        if (!active) return;
        const msg = err.response?.data?.detail || 'Error al confirmar el pago';
        setErrorMsg(msg);
        setStatus('error');
      }
    };

    confirmPayment();

    return () => { active = false; };
  }, [searchParams]);

  const handleGoToReservations = () => {
    sessionStorage.removeItem('paymentResult');
    navigate('/my-reservations');
  };

  if (status === 'loading') {
    return (
      <div className="min-h-screen pt-24 px-4 bg-background flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-primary animate-spin mx-auto mb-4" />
          <p className="text-lg text-foreground/70">Confirmando tu pago...</p>
        </div>
      </div>
    );
  }

  if (status === 'error') {
    return (
      <div className="min-h-screen pt-24 px-4 bg-background flex items-center justify-center">
        <div className="glass-panel p-8 rounded-2xl max-w-md w-full text-center">
          <div className="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <XCircle className="w-10 h-10 text-red-500" />
          </div>
          <h2 className="text-2xl font-bold text-foreground mb-2">Error en el pago</h2>
          <p className="text-foreground/70 mb-6">{errorMsg}</p>
          <button
            onClick={() => navigate('/')}
            className="w-full bg-primary hover:bg-secondary text-white font-medium py-2 px-6 rounded-lg transition-colors cursor-pointer"
          >
            Volver al inicio
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen pt-24 px-4 bg-background">
      <div className="max-w-lg mx-auto">
        <div className="glass-panel p-8 rounded-2xl text-center">
          <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <CheckCircle className="w-10 h-10 text-green-600" />
          </div>
          <h2 className="text-2xl font-bold text-foreground mb-2">¡Pago Exitoso!</h2>
          <p className="text-foreground/70 mb-6">Tu reserva ha sido confirmada</p>

          <div className="bg-white/50 rounded-xl p-4 mb-6">
            <p className="text-sm text-foreground/60 mb-1">Código de reserva</p>
            <p className="text-2xl font-bold text-primary tracking-widest">
              {result?.reservation_code}
            </p>
          </div>

          <div className="space-y-3 text-left bg-white/30 rounded-xl p-4 mb-6">
            <div className="flex justify-between text-sm">
              <span className="text-foreground/70">Asientos</span>
              <span className="font-medium text-foreground">{result?.seats_reserved}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-foreground/70">Total pagado</span>
              <span className="font-medium text-foreground">
                ${Number(result?.total_price).toFixed(2)}
              </span>
            </div>
          </div>

          <button
            onClick={handleGoToReservations}
            className="w-full bg-primary hover:bg-secondary text-white font-medium py-3 px-4 rounded-lg transition-colors cursor-pointer flex items-center justify-center gap-2"
          >
            <CalendarClock className="w-5 h-5" />
            Ver mis reservas
          </button>
        </div>
      </div>
    </div>
  );
}
