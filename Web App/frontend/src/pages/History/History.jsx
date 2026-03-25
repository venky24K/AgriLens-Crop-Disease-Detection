import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, Filter, Calendar, ChevronRight, FileText, Download, Trash2, Loader2, Leaf } from 'lucide-react';
import GlassCard from '../../components/GlassCard';
import GlassButton from '../../components/GlassButton';
import { useAuth } from '../../context/AuthContext';
import axios from 'axios';

const History = () => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('All');
  const [searchTerm, setSearchTerm] = useState('');
  const { user } = useAuth();

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const config = {
          headers: {
            Authorization: `Bearer ${user.token}`,
          },
        };
        const response = await axios.get('http://localhost:5000/api/history', config);
        setHistory(response.data);
      } catch (err) {
        console.error('Failed to fetch history:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, [user.token]);

  const filteredHistory = history.filter(item => {
    const matchesFilter = filter === 'All' || item.status === filter;
    const matchesSearch = item.disease.toLowerCase().includes(searchTerm.toLowerCase()) || 
                          item.status.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  const categories = ['All', 'Healthy', 'Diseased'];

  return (
    <div className="space-y-8">
      <header className="flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div>
          <h1 className="text-4xl font-black mb-2">Scan History</h1>
          <p className="text-teal-900/60 dark:text-white/60 font-medium">Review and manage your previous crop health diagnostics.</p>
        </div>
        
        <div className="flex flex-wrap gap-3">
          {categories.map(cat => (
            <button
              key={cat}
              onClick={() => setFilter(cat)}
              className={`px-5 py-2 rounded-full text-sm font-bold transition-all duration-300 ${
                filter === cat 
                  ? 'accent-gradient text-white shadow-lg' 
                  : 'bg-white/40 dark:bg-black/40 text-teal-900/60 dark:text-white/60 hover:bg-white/60'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </header>

      {/* Search and Filters */}
      <GlassCard className="!p-4" hover={false}>
        <div className="relative">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-teal-900/30 dark:text-white/30" size={20} />
          <input
            type="text"
            placeholder="Search by disease or status..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-12 pr-4 py-3 bg-white/30 dark:bg-black/30 border border-white/20 dark:border-white/10 rounded-2xl focus:outline-none focus:ring-2 focus:ring-accentGradientStart transition-all"
          />
        </div>
      </GlassCard>

      {loading ? (
        <div className="flex flex-col items-center justify-center py-24 space-y-4">
          <Loader2 className="animate-spin text-accentGradientStart" size={48} />
          <p className="font-bold text-teal-900/40 dark:text-white/40 uppercase tracking-widest">Retrieving Records...</p>
        </div>
      ) : filteredHistory.length > 0 ? (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          <AnimatePresence>
            {filteredHistory.map((item, index) => (
              <motion.div
                key={item._id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.95 }}
                transition={{ duration: 0.4, delay: index * 0.05 }}
              >
                <GlassCard className="h-full flex flex-col group p-0 overflow-hidden">
                  {/* Image Preview */}
                  <div className="h-48 relative overflow-hidden">
                    <img 
                      src={`http://localhost:5000${item.imageUrl}`} 
                      alt={item.disease} 
                      className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700" 
                    />
                    <div className={`absolute top-4 right-4 px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-wider backdrop-blur-md border border-white/20 ${
                      item.status === 'Healthy' 
                      ? 'bg-green-500/80 text-white' 
                      : 'bg-red-500/80 text-white'
                    }`}>
                      {item.status}
                    </div>
                  </div>

                  {/* Content */}
                  <div className="p-6 flex-1 space-y-4">
                    <div>
                      <h3 className="text-xl font-black truncate">{item.disease === 'None' ? 'Healthy Plant' : item.disease}</h3>
                      <div className="flex items-center gap-2 text-teal-900/40 dark:text-white/40 text-xs mt-1 font-bold">
                        <Calendar size={12} />
                        {new Date(item.createdAt).toLocaleDateString(undefined, { day: 'numeric', month: 'short', year: 'numeric' })}
                      </div>
                    </div>

                    <div className="flex items-center justify-between pt-4 border-t border-white/10">
                      <div className="space-y-1">
                        <p className="text-[10px] font-bold uppercase tracking-widest text-teal-900/30 dark:text-white/30">Confidence</p>
                        <p className="text-lg font-black text-accentGradientStart">{(item.confidence * 100).toFixed(0)}%</p>
                      </div>
                      <div className="flex gap-2">
                        <button className="p-2 rounded-xl bg-white/30 dark:bg-black/30 hover:bg-accentGradientStart hover:text-white transition-all duration-300">
                          <Download size={18} />
                        </button>
                        <button className="p-2 rounded-xl bg-white/30 dark:bg-black/30 hover:bg-red-500 hover:text-white transition-all duration-300">
                          <Trash2 size={18} />
                        </button>
                      </div>
                    </div>
                  </div>
                </GlassCard>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      ) : (
        <GlassCard className="py-24 text-center space-y-4">
          <div className="w-20 h-20 mx-auto rounded-3xl bg-white/50 dark:bg-black/50 flex items-center justify-center shadow-xl">
            <Leaf className="text-teal-900/20 dark:text-white/20" size={40} />
          </div>
          <h3 className="text-2xl font-black">No Records Found</h3>
          <p className="text-teal-900/60 dark:text-white/60 max-w-xs mx-auto">
            Try adjusting your search or start a new scan on the dashboard.
          </p>
          <GlassButton variant="secondary" className="mx-auto mt-4 px-8">
            Go to Dashboard
          </GlassButton>
        </GlassCard>
      )}
    </div>
  );
};

export default History;
