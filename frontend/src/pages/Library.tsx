import { useEffect, useState } from 'react';
import api from '../lib/api';
import { Download, Film, Loader2, FolderOpen, Play, Trash2, X } from 'lucide-react';

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
  const [deleteId, setDeleteId] = useState<number | null>(null);
  const [deleting, setDeleting] = useState(false);

  const fetchCompleted = async () => {
    try {
      const res = await api.get('/api/jobs/completed');
      setItems(res.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCompleted();
  }, []);

  const handleDelete = async () => {
    if (!deleteId) return;
    setDeleting(true);
    try {
      await api.delete(`/api/jobs/${deleteId}`);
      setItems((prev) => prev.filter((item) => item.id !== deleteId));
      setDeleteId(null);
    } catch (e) {
      console.error(e);
    } finally {
      setDeleting(false);
    }
  };

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
            <div key={item.id} className="bg-gray-900 border border-gray-800 rounded-2xl overflow-hidden group hover:border-indigo-500/50 transition-all shadow-lg hover:shadow-indigo-500/10">
              <div className="aspect-video bg-gray-800 flex items-center justify-center relative overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-t from-gray-900 via-gray-900/40 to-transparent opacity-80 group-hover:opacity-60 transition-opacity z-10"></div>
                <Film className="w-12 h-12 text-white/50 group-hover:text-white/90 group-hover:scale-110 transition-all z-20 absolute" />
                <button
                  onClick={() => setDeleteId(item.id)}
                  className="absolute top-2 right-2 z-30 p-2 bg-red-500/80 hover:bg-red-500 rounded-lg opacity-0 group-hover:opacity-100 transition-all"
                  title="Delete"
                >
                  <Trash2 className="w-4 h-4 text-white" />
                </button>
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
                  <div className="flex items-center gap-1.5">
                    <a
                      href={item.download_url}
                      target="_blank"
                      rel="noreferrer"
                      className="flex items-center gap-1 text-xs text-emerald-400 bg-emerald-400/10 border border-emerald-400/20 px-2.5 py-1.5 rounded-md hover:bg-emerald-400/20 transition-colors"
                      title="Play"
                    >
                      <Play className="w-3 h-3" />
                    </a>
                    <a
                      href={item.download_url}
                      download
                      className="flex items-center gap-1 text-xs text-indigo-400 bg-indigo-400/10 border border-indigo-400/20 px-2.5 py-1.5 rounded-md hover:bg-indigo-400/20 transition-colors"
                      onClick={(e) => e.stopPropagation()}
                      title="Download"
                    >
                      <Download className="w-3 h-3" />
                    </a>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Delete confirmation modal */}
      {deleteId !== null && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setDeleteId(null)}></div>
          <div className="relative bg-gray-900 border border-gray-800 rounded-2xl p-6 w-full max-w-md shadow-2xl">
            <button
              onClick={() => setDeleteId(null)}
              className="absolute top-4 right-4 p-1 text-gray-500 hover:text-white transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 bg-red-500/10 rounded-xl">
                <Trash2 className="w-6 h-6 text-red-400" />
              </div>
              <h2 className="text-lg font-semibold text-white">Delete Media</h2>
            </div>
            <p className="text-gray-400 text-sm mb-6">
              This will permanently delete the file from the server. This action cannot be undone.
            </p>
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => setDeleteId(null)}
                className="px-4 py-2 text-sm text-gray-300 bg-gray-800 hover:bg-gray-700 rounded-xl transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleDelete}
                disabled={deleting}
                className="px-4 py-2 text-sm text-white bg-red-600 hover:bg-red-500 disabled:bg-red-600/50 rounded-xl transition-colors flex items-center gap-2"
              >
                {deleting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Trash2 className="w-4 h-4" />}
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
