import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Mail, Lock, User, Eye, EyeOff, Loader2, ArrowRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import GlassCard from '../../components/GlassCard';
import GlassButton from '../../components/GlassButton';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';
import axios from 'axios';

const LoginSignup = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: ''
  });

  const navigate = useNavigate();
  const { login } = useAuth();
  const { addToast } = useToast();

  const handleInputChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    if (error) setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const endpoint = isLogin ? '/api/auth/login' : '/api/auth/signup';
      const response = await axios.post(`http://localhost:5000${endpoint}`, formData);
      
      login(response.data);
      addToast(isLogin ? 'Successfully logged in!' : 'Account created successfully!', 'success');
      navigate('/dashboard');
    } catch (err) {
      const msg = err.response?.data?.message || 'Something went wrong. Please try again.';
      setError(msg);
      addToast(msg, 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto py-12">
      <GlassCard className="!p-8">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-black mb-2">
            {isLogin ? 'Welcome Back' : 'Join AgriLens'}
          </h2>
          <p className="text-teal-900/60 dark:text-white/60">
            {isLogin ? 'Sign in to monitor your crop health' : 'Create an account to start scanning'}
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <AnimatePresence mode="wait">
            {!isLogin && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="space-y-2"
              >
                <label className="text-sm font-semibold ml-1">Full Name</label>
                <div className="relative">
                  <User className="absolute left-4 top-1/2 -translate-y-1/2 text-teal-500" size={18} />
                  <input
                    type="text"
                    name="name"
                    required={!isLogin}
                    value={formData.name}
                    onChange={handleInputChange}
                    placeholder="John Doe Brandon"
                    className="w-full pl-12 pr-4 py-3 bg-white/50 dark:bg-black/50 border border-white/20 dark:border-white/10 rounded-2xl focus:outline-none focus:ring-2 focus:ring-accentGradientStart transition-all"
                  />
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          <div className="space-y-2">
            <label className="text-sm font-semibold ml-1">Email Address</label>
            <div className="relative">
              <Mail className="absolute left-4 top-1/2 -translate-y-1/2 text-teal-500" size={18} />
              <input
                type="email"
                name="email"
                required
                value={formData.email}
                onChange={handleInputChange}
                placeholder="john@example.com"
                className="w-full pl-12 pr-4 py-3 bg-white/50 dark:bg-black/50 border border-white/20 dark:border-white/10 rounded-2xl focus:outline-none focus:ring-2 focus:ring-accentGradientStart transition-all"
              />
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-semibold ml-1">Password</label>
            <div className="relative">
              <Lock className="absolute left-4 top-1/2 -translate-y-1/2 text-teal-500" size={18} />
              <input
                type={showPassword ? 'text' : 'password'}
                name="password"
                required
                value={formData.password}
                onChange={handleInputChange}
                placeholder="••••••••"
                className="w-full pl-12 pr-12 py-3 bg-white/50 dark:bg-black/50 border border-white/20 dark:border-white/10 rounded-2xl focus:outline-none focus:ring-2 focus:ring-accentGradientStart transition-all"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-4 top-1/2 -translate-y-1/2 text-teal-900/40 dark:text-white/40 hover:text-teal-900 dark:hover:text-white transition-colors"
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
          </div>

          {error && (
            <motion.div
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              className="text-red-500 text-sm font-medium bg-red-100/50 dark:bg-red-900/20 p-3 rounded-xl border border-red-200/50"
            >
              {error}
            </motion.div>
          )}

          <GlassButton type="submit" className="w-full py-4 text-lg" onClick={handleSubmit}>
            {loading ? <Loader2 className="animate-spin" /> : (isLogin ? 'Sign In' : 'Create Account')}
            {!loading && <ArrowRight size={20} />}
          </GlassButton>
        </form>

        <div className="mt-8 pt-6 border-t border-white/20 dark:border-white/10 text-center">
          <p className="text-teal-900/60 dark:text-white/60">
            {isLogin ? "Don't have an account?" : "Already have an account?"}
            <button
              onClick={() => setIsLogin(!isLogin)}
              className="ml-2 font-bold text-teal-700 dark:text-accentGradientStart hover:underline"
            >
              {isLogin ? 'Sign Up Free' : 'Sign In Now'}
            </button>
          </p>
        </div>
      </GlassCard>
    </div>
  );
};

export default LoginSignup;
