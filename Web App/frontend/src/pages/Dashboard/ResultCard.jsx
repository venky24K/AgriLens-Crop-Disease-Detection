import React from 'react';
import { motion } from 'framer-motion';
import { CheckCircle2, AlertCircle, Calendar, ShieldCheck } from 'lucide-react';
import GlassCard from '../../components/GlassCard';

const ResultCard = ({ result }) => {
  if (!result) return null;

  const isHealthy = result.status === 'Healthy';

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9, y: 20 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      transition={{ duration: 0.5, type: 'spring' }}
      className="w-full max-w-2xl mx-auto mt-12"
    >
      <GlassCard className="relative overflow-hidden group">
        {/* Animated background glow */}
        <div className={`absolute top-0 right-0 w-32 h-32 blur-3xl opacity-20 -mr-16 -mt-16 transition-colors duration-500 ${isHealthy ? 'bg-green-400' : 'bg-red-400'}`}></div>

        <div className="flex flex-col md:flex-row gap-8 items-center">
          {/* Image Preview */}
          <div className="w-full md:w-48 h-48 rounded-2xl overflow-hidden border-2 border-white/20 dark:border-white/10 shadow-inner">
            <img 
              src={`http://localhost:5000${result.imageUrl}`} 
              alt="Scan Preview" 
              className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
            />
          </div>

          {/* Analysis Details */}
          <div className="flex-1 space-y-4 text-center md:text-left">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div>
                <h3 className="text-sm font-bold uppercase tracking-widest text-teal-900/40 dark:text-white/40 mb-1">Analysis Result</h3>
                <h2 className="text-3xl font-black text-teal-900 dark:text-white">
                  {isHealthy ? 'Healthy Plant' : result.disease}
                </h2>
              </div>
              <div className={`px-4 py-2 rounded-full flex items-center gap-2 font-bold text-sm ${isHealthy ? 'bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400' : 'bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-400'}`}>
                {isHealthy ? <CheckCircle2 size={18} /> : <AlertCircle size={18} />}
                {result.status}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="bg-white/30 dark:bg-black/20 p-3 rounded-2xl border border-white/10">
                <p className="text-xs font-medium text-teal-900/40 dark:text-white/40 mb-1">Confidence Score</p>
                <p className="text-xl font-black text-accentGradientStart">{(result.confidence * 100).toFixed(1)}%</p>
              </div>
              <div className="bg-white/30 dark:bg-black/20 p-3 rounded-2xl border border-white/10">
                <p className="text-xs font-medium text-teal-900/40 dark:text-white/40 mb-1">Detection Date</p>
                <div className="flex items-center gap-2 text-teal-900/60 dark:text-white/60">
                   <Calendar size={14} />
                   <span className="text-xs font-bold">{new Date().toLocaleDateString()}</span>
                </div>
              </div>
            </div>

            {!isHealthy && (
              <div className="mt-4 space-y-4">
                <div className="p-4 rounded-2xl bg-orange-50 dark:bg-orange-900/20 border border-orange-200/30 flex items-start gap-3">
                  <ShieldCheck size={20} className="text-orange-500 shrink-0 mt-0.5" />
                  <div>
                    <p className="text-xs font-bold text-orange-900 dark:text-orange-100 mb-1">Diagnosis Explanation</p>
                    <p className="text-xs text-orange-800 dark:text-orange-200 leading-relaxed font-medium">
                      {result.explanation || `We've identified potential ${result.disease}.`}
                    </p>
                  </div>
                </div>

                {result.treatment && result.treatment.length > 0 && (
                  <div className="p-4 rounded-2xl bg-teal-50 dark:bg-teal-900/20 border border-teal-200/30">
                    <p className="text-xs font-bold text-teal-900 dark:text-teal-100 mb-2 uppercase tracking-tighter">Recommended Treatment Plan</p>
                    <ul className="space-y-2">
                      {result.treatment.map((step, index) => (
                        <li key={index} className="flex items-start gap-2 text-xs text-teal-800 dark:text-teal-200 font-medium">
                          <span className="w-4 h-4 rounded-full bg-teal-500 text-white flex items-center justify-center text-[10px] shrink-0 mt-0.5">{index + 1}</span>
                          {step}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </GlassCard>
    </motion.div>
  );
};

export default ResultCard;
