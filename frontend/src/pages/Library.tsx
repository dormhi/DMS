import { useEffect, useState } from 'react';
import axios from 'axios';
import { Download, Film, Loader2, FolderOpen } from 'lucide-react';

interface CompletedJob {
  id: number;
  original_url: string;
  filename: string;
  download_url: string;
  created_at: string;
}

export function Library() {
  const [items, setItems] = useState<CompletedJob[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCompleted = async () => {
      try {
        const res = await axios.get('/api/jobs/completed');
        setItems(res.data);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    fetchCompleted();
  }, []);

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <div>
        <h1 className="text-3xl font-bold text-white tracking-tight">Media Library</h1>
        <p className="text-gray-400 mt-1">Browse and download your processed media.</p>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <Loader2 className="w-8 h-8 text-indigo-500 animate-spin" />
        </div>
      ) : items.length === 0 ? (
        <div className="bg-gray-900 border border-gray-800 border-dashed rounded-2xl p-16 text-center">
          <FolderOpen className="w-12 h-12 text-gray-700 mx-auto mb-3" />
          <p className="text-gray-400 text-lg">No completed media found.</p>
          <p className="text-gray-500 text-sm mt-1">Submit a URL from Telegram or the Dashboard to get started.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {items.map(item => (
            <div key={item.id} className="bg-gray-900 border border-gray-800 rounded-2xl overflow-hidden group cursor-pointer hover:border-indigo-500/50 transition-all shadow-lg hover:shadow-indigo-500/10">
              <div className="aspect-video bg-gray-800 flex items-center justify-center relative overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-t from-gray-900 via-gray-900/40 to-transparent opacity-80 group-hover:opacity-60 transition-opacity z-10"></div>
                <Film className="w-12 h-12 text-white/50 group-hover:text-white/90 group-hover:scale-110 transition-all z-20 absolute" />
              </div>
              <div className="p-5">
                <h3 className="font-medium text-gray-200 group-hover:text-indigo-400 transition-colors truncate" title={item.filename}>
                  {item.filename}
                </h3>
                <p className="text-xs text-gray-500 mt-1 truncate" title={item.original_url}>
                  {item.original_url}
                </p>
                <div className="flex items-center justify-between mt-3">
                  <p className="text-xs text-gray-500 bg-gray-800 px-2 py-1 rounded-md">
                    {new Date(item.created_at).toLocaleDateString()}
                  </p>
                  <a
                    href={item.download_url}
                    download
                    className="flex items-center gap-1.5 text-xs text-indigo-400 bg-indigo-400/10 border border-indigo-400/20 px-3 py-1.5 rounded-md hover:bg-indigo-400/20 transition-colors"
                    onClick={(e) => e.stopPropagation()}
                  >
                    <Download className="w-3.5 h-3.5" />
                    Download
                  </a>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
