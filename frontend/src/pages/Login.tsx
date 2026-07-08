import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Activity, Lock, User, Loader2 } from 'lucide-react';

export function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);

      const res = await axios.post('/api/login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });

      localStorage.setItem('dms_token', res.data.access_token);
      navigate('/');
    } catch (err: any) {
      if (err.response?.status === 401) {
        setError('Kullanıcı adı veya şifre hatalı.');
      } else {
        setError('Sunucuya bağlanılamadı.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-950 relative overflow-hidden">
      {/* Background glow */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-indigo-500/10 rounded-full blur-[120px]"></div>
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-[120px]"></div>

      <div className="relative z-10 w-full max-w-md p-8 bg-gray-900/80 backdrop-blur-xl border border-gray-800 rounded-2xl shadow-2xl">
        <div className="flex flex-col items-center mb-8">
          <div className="p-3 bg-indigo-500/10 border border-indigo-500/20 rounded-2xl mb-4">
            <Activity className="w-8 h-8 text-indigo-400" />
          </div>
          <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 to-purple-400">
            DMS Portal
          </h1>
          <p className="text-gray-500 mt-2 text-sm">Dormhi Media Server</p>
        </div>

        <form onSubmit={handleLogin} className="space-y-5">
          {error && (
            <div className="bg-red-500/10 border border-red-500/20 text-red-400 px-4 py-3 rounded-xl text-sm text-center">
              {error}
            </div>
          )}

          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none">
              <User className="w-4 h-4 text-gray-500" />
            </div>
            <input
              type="text"
              className="w-full bg-gray-800/50 border border-gray-700 text-white rounded-xl px-4 py-3 pl-10 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500/50 transition-all placeholder-gray-500"
              placeholder="Kullanıcı adı"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              autoFocus
            />
          </div>

          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none">
              <Lock className="w-4 h-4 text-gray-500" />
            </div>
            <input
              type="password"
              className="w-full bg-gray-800/50 border border-gray-700 text-white rounded-xl px-4 py-3 pl-10 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500/50 transition-all placeholder-gray-500"
              placeholder="Şifre"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-600/50 text-white font-medium rounded-xl px-4 py-3 transition-all duration-300 shadow-lg shadow-indigo-500/20 hover:shadow-indigo-500/40 flex items-center justify-center"
          >
            {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Giriş Yap'}
          </button>
        </form>
      </div>
    </div>
  );
}
