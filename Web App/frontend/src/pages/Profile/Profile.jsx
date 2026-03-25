import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { User, Mail, Calendar, Shield, Settings, LogOut, Camera, Award, Save, X } from 'lucide-react';
import GlassCard from '../../components/GlassCard';
import GlassButton from '../../components/GlassButton';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';
import axios from 'axios';

const Profile = () => {
  const { user, logout, updateUser } = useAuth();
  const { showToast } = useToast();
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    name: user?.name || '',
    email: user?.email || ''
  });
  const [isSaving, setIsSaving] = useState(false);

  if (!user) return null;

  const handleSave = async () => {
    try {
      setIsSaving(true);
      const config = {
        headers: {
          Authorization: `Bearer ${user.token}`,
        },
      };
      const { data } = await axios.put('http://localhost:5000/api/user/profile', formData, config);
      updateUser(data);
      showToast('Profile updated successfully!', 'success');
      setIsEditing(false);
    } catch (error) {
      showToast(error.response?.data?.message || 'Failed to update profile', 'error');
    } finally {
      setIsSaving(false);
    }
  };

  const stats = [
    { label: 'Total Scans', value: '24', icon: <Camera size={18} className="text-blue-500" /> },
    { label: 'Health Score', value: '92%', icon: <Award size={18} className="text-accentGradientStart" /> },
    { label: 'Member Since', value: 'Mar 2026', icon: <Calendar size={18} className="text-purple-500" /> },
  ];

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <header>
        <h1 className="text-4xl font-black mb-2">User Profile</h1>
        <p className="text-teal-900/60 dark:text-white/60 font-medium">Manage your account and view your agricultural impact.</p>
      </header>

      <div className="grid md:grid-cols-3 gap-8">
        {/* Profile Card */}
        <div className="md:col-span-1 space-y-6">
          <GlassCard className="text-center p-8">
            <div className="relative inline-block mb-6">
              <div className="w-32 h-32 rounded-3xl overflow-hidden border-4 border-white dark:border-black shadow-2xl mx-auto">
                <img 
                  src={user.profilePic || 'https://cdn-icons-png.flaticon.com/512/149/149071.png'} 
                  alt={user.name} 
                  className="w-full h-full object-cover"
                />
              </div>
              <button className="absolute bottom-1 right-1 p-2 accent-gradient text-white rounded-xl shadow-lg hover:scale-110 transition-transform">
                <Camera size={16} />
              </button>
            </div>
            
            {isEditing ? (
              <input 
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full bg-white/30 dark:bg-black/30 border border-white/20 rounded-xl px-4 py-2 text-center font-black focus:outline-none focus:border-accentGradientStart"
              />
            ) : (
              <h2 className="text-2xl font-black">{user.name}</h2>
            )}
            <p className="text-teal-900/40 dark:text-white/40 text-sm font-bold uppercase tracking-widest mt-1">Verified Member</p>
            
            <div className="mt-8 pt-6 border-t border-white/10 space-y-3">
              {isEditing ? (
                <div className="flex gap-2">
                  <GlassButton 
                    className="flex-1 py-3 text-sm accent-gradient" 
                    onClick={handleSave}
                    disabled={isSaving}
                  >
                    <Save size={18} /> {isSaving ? 'Saving...' : 'Save'}
                  </GlassButton>
                  <GlassButton 
                    variant="secondary" 
                    className="p-3 text-sm" 
                    onClick={() => {
                        setIsEditing(false);
                        setFormData({ name: user.name, email: user.email });
                    }}
                  >
                    <X size={18} />
                  </GlassButton>
                </div>
              ) : (
                <GlassButton variant="secondary" className="w-full py-3 text-sm" onClick={() => setIsEditing(true)}>
                  <Settings size={18} /> Edit Profile
                </GlassButton>
              )}
              <GlassButton variant="outline" className="w-full py-3 text-sm text-red-500 border-red-500/30 hover:bg-red-500/10" onClick={logout}>
                <LogOut size={18} /> Logout Session
              </GlassButton>
            </div>
          </GlassCard>
        </div>

        {/* Details & Stats */}
        <div className="md:col-span-2 space-y-8">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {stats.map((stat, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <GlassCard className="text-center !p-4">
                  <div className="w-10 h-10 rounded-xl bg-white/50 dark:bg-black/50 flex items-center justify-center mx-auto mb-3">
                    {stat.icon}
                  </div>
                  <p className="text-[10px] font-bold uppercase tracking-widest text-teal-900/30 dark:text-white/30">{stat.label}</p>
                  <p className="text-xl font-black">{stat.value}</p>
                </GlassCard>
              </motion.div>
            ))}
          </div>

          <GlassCard className="space-y-6">
            <h3 className="text-xl font-black flex items-center gap-2">
              <Shield size={22} className="text-accentGradientStart" /> Account Security
            </h3>
            
            <div className="space-y-6">
              <div className="flex items-center justify-between p-4 bg-white/30 dark:bg-black/30 rounded-2xl border border-white/10">
                <div className="flex items-center gap-4 flex-1">
                  <div className="p-3 rounded-xl bg-teal-100 dark:bg-teal-900/30 text-teal-600">
                    <Mail size={20} />
                  </div>
                  <div className="flex-1">
                    <p className="text-xs font-bold text-teal-900/40 dark:text-white/40 uppercase tracking-widest">Email Address</p>
                    {isEditing ? (
                      <input 
                        type="email"
                        value={formData.email}
                        onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                        className="w-full bg-transparent border-b border-accentGradientStart focus:outline-none font-bold py-1"
                      />
                    ) : (
                      <p className="font-bold">{user.email}</p>
                    )}
                  </div>
                </div>
                {!isEditing && (
                  <button onClick={() => setIsEditing(true)} className="text-sm font-bold text-accentGradientStart hover:underline ml-4">Change</button>
                )}
              </div>
            </div>
          </GlassCard>
        </div>
      </div>
    </div>
  );
};

export default Profile;
