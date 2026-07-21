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

/*function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="min-h-screen flex items-center justify-center">Cargando...</div>;
  if (!user) return <Navigate to="/login" replace />;
  return <>{children}</>;
}*/

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  return <>{children}</>; // bypass temporal, revertir después
}


function App() {
  return (
    <AuthProvider>
      <Router>
        <Navbar />
        <Routes>
          <Route path="/" element={<ProtectedRoute><SearchPage /></ProtectedRoute>} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/payment-success" element={<ProtectedRoute><PaymentSuccessPage /></ProtectedRoute>} />
          <Route path="/my-reservations" element={<ProtectedRoute><MyReservationsPage /></ProtectedRoute>} />
          <Route path="/vehicles" element={<ProtectedRoute><MyVehiclesPage /></ProtectedRoute>} />
          <Route path="/publish" element={<ProtectedRoute><PublishTripPage /></ProtectedRoute>} />
          <Route path="/trips/:id" element={<ProtectedRoute><TripDetailPage /></ProtectedRoute>} />
        </Routes>
        <ToastContainer position="bottom-right" theme="colored" />
      </Router>
    </AuthProvider>
  );
}

export default App;
