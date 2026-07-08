import { Routes, Route, Navigate } from 'react-router-dom';
import { Sidebar } from './components/Sidebar';
import { Dashboard } from './pages/Dashboard';
import { Library } from './pages/Library';
import { Login } from './pages/Login';

function ProtectedLayout({ children }: { children: React.ReactNode }) {
  const token = localStorage.getItem('dms_token');
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return (
    <div className="flex h-screen bg-gray-950 font-sans">
      <Sidebar />
      <main className="flex-1 overflow-y-auto p-8">
        {children}
      </main>
    </div>
  );
}

function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/" element={<ProtectedLayout><Dashboard /></ProtectedLayout>} />
      <Route path="/library" element={<ProtectedLayout><Library /></ProtectedLayout>} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
