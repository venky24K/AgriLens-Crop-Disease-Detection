import React from 'react';
import { motion } from 'framer-motion';

const GlassButton = ({ 
  children, 
  onClick, 
  className = '', 
  type = 'button',
  variant = 'primary' // primary, secondary, outline
}) => {
  const variants = {
    primary: 'accent-gradient text-white shadow-lg glowing-hover',
    secondary: 'bg-white/20 dark:bg-black/20 text-teal-900 dark:text-white backdrop-blur-md border border-white/30',
    outline: 'bg-transparent border-2 border-accentGradientStart text-teal-900 dark:text-white hover:bg-accentGradientStart/10'
  };

  return (
    <motion.button
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      type={type}
      onClick={onClick}
      className={`px-6 py-3 rounded-full font-semibold transition-all duration-300 flex items-center justify-center gap-2 ${variants[variant]} ${className}`}
    >
      {children}
    </motion.button>
  );
};

export default GlassButton;
