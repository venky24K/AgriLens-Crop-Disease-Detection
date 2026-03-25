import React from 'react';
import { motion } from 'framer-motion';

const GlassCard = ({ children, className = '', hover = true }) => {
  return (
    <motion.div
      whileHover={hover ? { y: -5, boxShadow: '0 20px 40px rgba(0,0,0,0.1)' } : {}}
      className={`glass-card p-6 ${className}`}
    >
      {children}
    </motion.div>
  );
};

export default GlassCard;
