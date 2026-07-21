import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

import Navbar from './components/Navbar';
import LoginPage from './pages/auth/LoginPage';
import RegisterPage from './pages/auth/RegisterPage';
import PaymentSuccessPage from './pages/booking/PaymentSuccessPage';
import MyReservationsPage from './pages/booking/MyReservationsPage';
import SearchPage from './pages/trips/SearchPage';
import PublishTripPage from './pages/trips/PublishTripPage';
import MyVehiclesPage from './pages/trips/MyVehiclesPage';
import TripDetailPage from './pages/trips/TripDetailPage';
import MyTripsPage from './pages/trips/MyTripsPage';
import GlobalChatPage from './pages/chat/GlobalChatPage';
import { useEffect } from 'react';
import { toast } from 'react-toastify';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="min-h-screen flex items-center justify-center">Cargando...</div>;
  if (!user) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

function RoleProtectedRoute({ children, role }: { children: React.ReactNode; role: string }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="min-h-screen flex items-center justify-center">Cargando...</div>;
  if (!user) return <Navigate to="/login" replace />;
  if (user.role !== role) return <Navigate to="/" replace />;
  return <>{children}</>;
}

function App() {
  useEffect(() => {
    const reason = localStorage.getItem('redirectReason');
    if (reason) {
      toast.error(reason);
      localStorage.removeItem('redirectReason');
    }
  }, []);

  return (
    <AuthProvider>
      <Router>
        <Navbar />
        <Routes>
          <Route path="/" element={<ProtectedRoute><SearchPage /></ProtectedRoute>} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/payment-success" element={<ProtectedRoute><PaymentSuccessPage /></ProtectedRoute>} />
          <Route path="/my-reservations" element={<RoleProtectedRoute role="pasajero"><MyReservationsPage /></RoleProtectedRoute>} />
          <Route path="/vehicles" element={<RoleProtectedRoute role="conductor"><MyVehiclesPage /></RoleProtectedRoute>} />
          <Route path="/publish" element={<RoleProtectedRoute role="conductor"><PublishTripPage /></RoleProtectedRoute>} />
          <Route path="/my-trips" element={<RoleProtectedRoute role="conductor"><MyTripsPage /></RoleProtectedRoute>} />
          <Route path="/chat" element={<ProtectedRoute><GlobalChatPage /></ProtectedRoute>} />
          <Route path="/trips/:id" element={<ProtectedRoute><TripDetailPage /></ProtectedRoute>} />
        </Routes>
        <ToastContainer position="bottom-right" theme="colored" />
      </Router>
    </AuthProvider>
  );
}

export default App;
