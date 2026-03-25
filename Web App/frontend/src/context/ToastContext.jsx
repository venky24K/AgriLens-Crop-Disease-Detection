import React, { createContext, useContext, useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, CheckCircle, AlertCircle, Info, Bell } from 'lucide-react';

const ToastContext = createContext();

export const ToastProvider = ({ children }) => {
  const [toasts, setToasts] = useState([]);

  const addToast = useCallback((message, type = 'info') => {
    const id = Math.random().toString(36).substr(2, 9);
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((toast) => toast.id !== id));
    }, 5000);
  }, []);

  const removeToast = useCallback((id) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id));
  }, []);

  return (
    <ToastContext.Provider value={{ addToast }}>
      {children}
      <div className="fixed bottom-6 right-6 z-[100] flex flex-col gap-3 pointer-events-none">
        <AnimatePresence>
          {toasts.map((toast) => (
            <motion.div
              key={toast.id}
              initial={{ opacity: 0, x: 50, scale: 0.9 }}
              animate={{ opacity: 1, x: 0, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9, transition: { duration: 0.2 } }}
              className="pointer-events-auto"
            >
              <div className={`flex items-center gap-4 px-6 py-4 rounded-2xl shadow-2xl backdrop-blur-xl border border-white/20 min-w-[300px] ${
                toast.type === 'success' ? 'bg-green-500/90 text-white' :
                toast.type === 'error' ? 'bg-red-500/90 text-white' :
                toast.type === 'warning' ? 'bg-orange-500/90 text-white' :
                'bg-white/90 dark:bg-black/90 text-teal-900 dark:text-white'
              }`}>
                {toast.type === 'success' && <CheckCircle size={20} />}
                {toast.type === 'error' && <AlertCircle size={20} />}
                {toast.type === 'warning' && <Bell size={20} />}
                {toast.type === 'info' && <Info size={20} className="text-blue-500" />}
                
                <p className="flex-1 font-bold text-sm">{toast.message}</p>
                
                <button onClick={() => removeToast(toast.id)} className="opacity-60 hover:opacity-100 transition-opacity">
                  <X size={16} />
                </button>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </ToastContext.Provider>
  );
};

export const useToast = () => useContext(ToastContext);
