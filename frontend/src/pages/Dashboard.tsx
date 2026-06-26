import { useEffect, useState } from 'react';
import axios from 'axios';
import { Clock, CheckCircle, AlertCircle, RefreshCw, Loader2 } from 'lucide-react';

interface Job {
  id: number;
  original_url: string;
  state: string;
  created_at: string;
}

export function Dashboard() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchJobs = async () => {
    try {
      const token = localStorage.getItem('dms_token');
      const res = await axios.get('http://localhost:8000/api/jobs', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setJobs(res.data);
    } catch (e) {
      console.error(e);
      if (axios.isAxiosError(e) && e.response?.status === 401) {
        localStorage.removeItem('dms_token');
        window.location.href = '/login';
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs();
    const interval = setInterval(fetchJobs, 3000);
    return () => clearInterval(interval);
  }, []);

  const getStateColor = (state: string) => {
    switch(state) {
      case 'completed': return 'text-emerald-400 bg-emerald-400/10 border-emerald-400/20';
      case 'failed': return 'text-red-400 bg-red-400/10 border-red-400/20';
      case 'processing': return 'text-amber-400 bg-amber-400/10 border-amber-400/20';
      case 'downloading': return 'text-blue-400 bg-blue-400/10 border-blue-400/20';
      default: return 'text-gray-400 bg-gray-400/10 border-gray-400/20';
    }
  };

  const getStateIcon = (state: string) => {
    switch(state) {
      case 'completed': return <CheckCircle className="w-4 h-4" />;
      case 'failed': return <AlertCircle className="w-4 h-4" />;
      case 'processing': 
      case 'downloading': return <RefreshCw className="w-4 h-4 animate-spin" />;
      default: return <Clock className="w-4 h-4" />;
    }
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <div>
        <h1 className="text-3xl font-bold text-white tracking-tight">Dashboard</h1>
        <p className="text-gray-400 mt-1">Real-time status of your media server jobs.</p>
      </div>

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
                      <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium border shadow-sm ${getStateColor(job.state)}`}>
                        {getStateIcon(job.state)}
                        <span className="capitalize">{job.state}</span>
                      </span>
                    </td>
                    <td className="px-6 py-4 text-gray-500">
                      {new Date(job.created_at).toLocaleString()}
                    </td>
                  </tr>
                ))}
                {jobs.length === 0 && (
                  <tr>
                    <td colSpan={4} className="px-6 py-12 text-center text-gray-500">
                      <div className="flex flex-col items-center justify-center">
                        <Clock className="w-12 h-12 text-gray-700 mb-3" />
                        <p>No active jobs found.</p>
                        <p className="text-sm mt-1">Send a link via Telegram to start!</p>
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
