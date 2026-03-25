import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Sun, Moon, Leaf, LayoutDashboard, History, User, LogOut } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';
import { useAuth } from '../context/AuthContext';

const Navbar = () => {
  const { isDarkMode, toggleTheme } = useTheme();
  const { user, logout } = useAuth();
  const location = useLocation();

  const navLinks = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'History', path: '/history', icon: History },
    { name: 'Profile', path: '/profile', icon: User },
  ];

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 px-6 py-4">
      <div className="max-w-7xl mx-auto flex items-center justify-between glass-card px-8 py-3 !rounded-full">
        <Link to="/" className="flex items-center gap-2 group">
          <div className="w-10 h-10 accent-gradient rounded-xl flex items-center justify-center shadow-lg group-hover:rotate-12 transition-transform duration-300">
            <Leaf className="text-white" size={24} />
          </div>
          <span className="text-xl font-bold bg-gradient-to-r from-teal-600 to-blue-600 bg-clip-text text-transparent">
            AgriLens
          </span>
        </Link>

        {user ? (
          <div className="hidden md:flex items-center gap-8">
            {navLinks.map((link) => (
              <Link
                key={link.path}
                to={link.path}
                className={`flex items-center gap-2 font-medium transition-colors duration-300 ${
                  location.pathname === link.path 
                    ? 'text-teal-600 dark:text-accentGradientStart' 
                    : 'text-teal-900/60 dark:text-white/60 hover:text-teal-600 dark:hover:text-white'
                }`}
              >
                <link.icon size={18} />
                {link.name}
              </Link>
            ))}
          </div>
        ) : null}

        <div className="flex items-center gap-4">
          <button
            onClick={toggleTheme}
            className="p-2 rounded-full bg-white/30 dark:bg-black/30 hover:bg-white/50 transition-colors"
          >
            {isDarkMode ? <Sun size={20} className="text-yellow-400" /> : <Moon size={20} className="text-teal-900" />}
          </button>

          {user ? (
            <button
              onClick={logout}
              className="p-2 rounded-full bg-red-100 dark:bg-red-900/30 text-red-600 hover:bg-red-200 transition-colors"
              title="Logout"
            >
              <LogOut size={20} />
            </button>
          ) : (
            <Link to="/login">
              <button className="accent-gradient text-white px-6 py-2 rounded-full font-medium hover:opacity-90 transition-opacity">
                Sign In
              </button>
            </Link>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
