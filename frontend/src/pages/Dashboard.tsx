import { useEffect, useState } from 'react';
import api from '../lib/api';
import { Clock, CheckCircle, AlertCircle, RefreshCw, Loader2, Upload, WifiOff, Send, LinkIcon } from 'lucide-react';

interface Job {
  id: number;
  original_url: string;
  state: string;
  error_message: string | null;
  created_at: string;
}

export function Dashboard() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [connectionError, setConnectionError] = useState(false);
  const [url, setUrl] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [submitMessage, setSubmitMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const fetchJobs = async () => {
    try {
      const res = await api.get('/api/jobs');
      setJobs(res.data);
      setConnectionError(false);
    } catch (e) {
      console.error(e);
      setConnectionError(true);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs();
    const interval = setInterval(fetchJobs, 3000);
    return () => clearInterval(interval);
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim() || submitting) return;

    setSubmitting(true);
    setSubmitMessage(null);

    try {
      const res = await api.post('/api/jobs/submit', { url: url.trim() });
      setSubmitMessage({ type: 'success', text: `✅ Görev eklendi! (Job #${res.data.id})` });
      setUrl('');
      fetchJobs();
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Görev gönderilemedi.';
      setSubmitMessage({ type: 'error', text: `❌ ${msg}` });
    } finally {
      setSubmitting(false);
      setTimeout(() => setSubmitMessage(null), 4000);
    }
  };

  const getStateColor = (state: string) => {
    switch(state) {
      case 'completed': return 'text-emerald-400 bg-emerald-400/10 border-emerald-400/20';
      case 'failed': return 'text-red-400 bg-red-400/10 border-red-400/20';
      case 'processing': return 'text-amber-400 bg-amber-400/10 border-amber-400/20';
      case 'downloading': return 'text-blue-400 bg-blue-400/10 border-blue-400/20';
      case 'uploading': return 'text-purple-400 bg-purple-400/10 border-purple-400/20';
      default: return 'text-gray-400 bg-gray-400/10 border-gray-400/20';
    }
  };

  const getStateIcon = (state: string) => {
    switch(state) {
      case 'completed': return <CheckCircle className="w-4 h-4" />;
      case 'failed': return <AlertCircle className="w-4 h-4" />;
      case 'uploading': return <Upload className="w-4 h-4 animate-pulse" />;
      case 'processing': 
      case 'downloading': return <RefreshCw className="w-4 h-4 animate-spin" />;
      default: return <Clock className="w-4 h-4" />;
    }
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <div>
        <h1 className="text-3xl font-bold text-white tracking-tight">Dashboard</h1>
        <p className="text-gray-400 mt-1">İndirme görevi gönder ve işlemleri canlı takip et.</p>
      </div>

      {/* URL Submit Form */}
      <form onSubmit={handleSubmit} className="bg-gray-900/80 border border-gray-800 rounded-2xl p-5 shadow-xl backdrop-blur-sm">
        <div className="flex gap-3">
          <div className="relative flex-1">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <LinkIcon className="w-4 h-4 text-gray-500" />
            </div>
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="Video linkini yapıştır (YouTube, Kick, Facebook...)"
              className="w-full bg-gray-800/50 border border-gray-700 text-white rounded-xl px-4 py-3 pl-11 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500/50 transition-all placeholder-gray-500"
              required
            />
          </div>
          <button
            type="submit"
            disabled={submitting || !url.trim()}
            className="bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-600/30 disabled:cursor-not-allowed text-white font-medium rounded-xl px-6 py-3 transition-all duration-300 shadow-lg shadow-indigo-500/20 hover:shadow-indigo-500/40 flex items-center gap-2 whitespace-nowrap"
          >
            {submitting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
            Gönder
          </button>
        </div>
        {submitMessage && (
          <div className={`mt-3 text-sm px-4 py-2.5 rounded-xl ${
            submitMessage.type === 'success' 
              ? 'bg-emerald-500/10 border border-emerald-500/20 text-emerald-400'
              : 'bg-red-500/10 border border-red-500/20 text-red-400'
          }`}>
            {submitMessage.text}
          </div>
        )}
      </form>

      {connectionError && (
        <div className="bg-red-500/10 border border-red-500/20 rounded-xl px-5 py-4 flex items-center gap-3">
          <WifiOff className="w-5 h-5 text-red-400 flex-shrink-0" />
          <div>
            <p className="text-red-400 font-medium text-sm">Backend bağlantısı kurulamıyor</p>
            <p className="text-red-400/60 text-xs mt-0.5">API sunucusuna ulaşılamıyor. Lütfen backend konteynerinin çalıştığından emin olun.</p>
          </div>
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <Loader2 className="w-8 h-8 text-indigo-500 animate-spin" />
        </div>
      ) : (
        <div className="bg-gray-900 border border-gray-800 rounded-2xl overflow-hidden shadow-xl">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-gray-300">
              <thead className="bg-gray-800/50 text-gray-400 border-b border-gray-800">
                <tr>
                  <th className="px-6 py-4 font-medium">Job ID</th>
                  <th className="px-6 py-4 font-medium">Media Source</th>
                  <th className="px-6 py-4 font-medium">Status</th>
                  <th className="px-6 py-4 font-medium">Date added</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800">
                {jobs.map(job => (
                  <tr key={job.id} className="hover:bg-gray-800/30 transition-colors group">
                    <td className="px-6 py-4 font-mono text-gray-500 group-hover:text-gray-400 transition-colors">#{job.id}</td>
                    <td className="px-6 py-4 max-w-xs truncate font-medium text-gray-200">{job.original_url}</td>
                    <td className="px-6 py-4">
                      <div className="flex flex-col gap-1">
                        <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium border shadow-sm w-fit ${getStateColor(job.state)}`}>
                          {getStateIcon(job.state)}
                          <span className="capitalize">{job.state}</span>
                        </span>
                        {job.state === 'failed' && job.error_message && (
                          <span className="text-xs text-red-400/70 truncate max-w-[200px]" title={job.error_message}>
                            {job.error_message}
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 text-gray-500">
                      {new Date(job.created_at).toLocaleString()}
                    </td>
                  </tr>
                ))}
                {jobs.length === 0 && !connectionError && (
                  <tr>
                    <td colSpan={4} className="px-6 py-12 text-center text-gray-500">
                      <div className="flex flex-col items-center justify-center">
                        <Clock className="w-12 h-12 text-gray-700 mb-3" />
                        <p>Henüz bir görev yok.</p>
                        <p className="text-sm mt-1">Yukarıdan link atarak veya Telegram'dan başlayabilirsiniz.</p>
                      </div>
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
