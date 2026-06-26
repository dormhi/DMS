import { Routes, Route } from 'react-router-dom';
import { Sidebar } from './components/Sidebar';
import { Dashboard } from './pages/Dashboard';
import { Library } from './pages/Library';

function App() {
  return (
    <div className="flex h-screen bg-gray-950 font-sans">
      <Sidebar />
      <main className="flex-1 overflow-y-auto p-8">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/library" element={<Library />} />
          <Route path="/settings" element={<div className="text-white">Settings Coming Soon</div>} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
