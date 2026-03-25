import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Navbar from './Navbar';

const Layout = ({ children }) => {
  return (
    <div className="min-h-screen relative overflow-hidden bg-white/40 dark:bg-[#0a0a0c] transition-colors duration-500">
      {/* User Background Image */}
      <div 
        className="fixed inset-0 pointer-events-none opacity-[0.2] dark:opacity-[0.15] z-0 contrast-[0.8] saturate-[0.8]"
        style={{
          backgroundImage: "url('/bg-image.png')",
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          filter: 'blur(1px)'
        }}
      ></div>
      
      {/* Background Decorative Blobs */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-accentGradientStart/20 blur-[120px] rounded-full animate-pulse-slow"></div>
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-accentGradientEnd/20 blur-[120px] rounded-full animate-pulse-slow delay-1000"></div>
      
      <Navbar />
      
      <main className="relative z-10 pt-32 pb-12 px-6 max-w-7xl mx-auto">
        <AnimatePresence mode="wait">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.5 }}
          >
            {children}
          </motion.div>
        </AnimatePresence>
      </main>
      
      {/* Footer / Branding Background Element */}
      <div className="fixed bottom-10 left-1/2 -translate-x-1/2 opacity-10 pointer-events-none text-8xl font-black uppercase tracking-widest whitespace-nowrap">
        Future of Farming
      </div>
    </div>
  );
};

export default Layout;
