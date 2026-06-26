import { PlayCircle } from 'lucide-react';

export function Library() {
  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <div>
        <h1 className="text-3xl font-bold text-white tracking-tight">Media Library</h1>
        <p className="text-gray-400 mt-1">Browse and download your processed media.</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {/* Placeholder for library items */}
        <div className="bg-gray-900 border border-gray-800 rounded-2xl overflow-hidden group cursor-pointer hover:border-indigo-500/50 transition-all shadow-lg hover:shadow-indigo-500/10">
          <div className="aspect-video bg-gray-800 flex items-center justify-center relative overflow-hidden">
             <div className="absolute inset-0 bg-gradient-to-t from-gray-900 via-gray-900/40 to-transparent opacity-80 group-hover:opacity-60 transition-opacity z-10"></div>
             <PlayCircle className="w-12 h-12 text-white/50 group-hover:text-white/90 group-hover:scale-110 transition-all z-20 absolute" />
             <div className="absolute bottom-3 right-3 bg-black/70 text-xs font-mono text-white px-2 py-1 rounded z-20">10:24</div>
          </div>
          <div className="p-5">
            <h3 className="font-medium text-gray-200 group-hover:text-indigo-400 transition-colors truncate">Sample_Video_Optimized.mp4</h3>
            <div className="flex items-center justify-between mt-3">
              <p className="text-xs text-gray-500 bg-gray-800 px-2 py-1 rounded-md">120 MB</p>
              <p className="text-xs text-emerald-400/80 bg-emerald-400/10 border border-emerald-400/20 px-2 py-1 rounded-md">h264 / aac</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
