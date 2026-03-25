import React, { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, X, Loader2, Image as ImageIcon, Sparkles } from 'lucide-react';
import GlassCard from '../../components/GlassCard';
import GlassButton from '../../components/GlassButton';
import ResultCard from './ResultCard';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';
import axios from 'axios';

const Dashboard = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const { user } = useAuth();
  const { addToast } = useToast();

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setResult(null);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setResult(null);
    }
  };

  const removeFile = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setResult(null);
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      addToast('Please select an image first', 'error');
      return;
    }

    if (!user || !user.token) {
      addToast('Authentication error. Please log in again.', 'error');
      console.error('User or token missing:', user);
      return;
    }

    setUploading(true);
    console.log('Starting upload to backend: http://localhost:5000/api/predict');
    
    const formData = new FormData();
    formData.append('image', selectedFile);

    try {
      const config = {
        headers: {
          'Content-Type': 'multipart/form-data',
          Authorization: `Bearer ${user.token}`,
        },
      };
      
      const response = await axios.post('http://localhost:5000/api/predict', formData, config);
      console.log('Prediction received successfully:', response.data);
      setResult(response.data);
      addToast('Analysis complete!', 'success');
    } catch (err) {
      const errorMsg = err.response?.data?.message || err.message || 'Unknown error';
      console.error('Upload failed details:', err);
      alert(`Upload failed: ${errorMsg}`);
      addToast(`Error: ${errorMsg}`, 'error');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto py-8">
      <header className="mb-12 text-center md:text-left">
        <h1 className="text-4xl font-black mb-2">Hello, {user?.name.split(' ')[0]} 👋</h1>
        <p className="text-teal-900/60 dark:text-white/60 font-medium">Ready to analyze your crops today?</p>
      </header>

      <div className="grid md:grid-cols-1 gap-8">
        <GlassCard 
          className={`relative border-2 border-dashed transition-all duration-300 ${
            isDragOver ? 'border-accentGradientStart bg-accentGradientStart/5' : 'border-white/30 dark:border-white/10'
          }`}
          hover={false}
        >
          <div 
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            className="flex flex-col items-center justify-center py-12 px-4"
          >
            {previewUrl ? (
              <div className="relative group">
                <img 
                  src={previewUrl} 
                  alt="Preview" 
                  className="max-h-64 rounded-2xl shadow-2xl border-4 border-white dark:border-black transition-transform group-hover:scale-[1.02]" 
                />
                <button 
                  onClick={removeFile}
                  className="absolute -top-3 -right-3 p-2 bg-red-500 text-white rounded-full shadow-lg hover:bg-red-600 transition-colors"
                >
                  <X size={20} />
                </button>
              </div>
            ) : (
              <>
                <div className="w-20 h-20 rounded-3xl bg-white/50 dark:bg-black/50 flex items-center justify-center mb-6 shadow-xl relative overflow-hidden group">
                  <div className="absolute inset-0 accent-gradient opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                  <Upload className="text-teal-600 dark:text-accentGradientStart group-hover:text-white transition-colors duration-300 relative z-10" size={32} />
                </div>
                <h3 className="text-xl font-bold mb-2">Upload Crop Image</h3>
                <p className="text-teal-900/40 dark:text-white/40 mb-8 text-center max-w-sm font-medium">
                  Drag and drop a clear photo of the leaf or click to browse files from your device.
                </p>
                <input
                  type="file"
                  id="file-upload"
                  className="hidden"
                  onChange={handleFileChange}
                  accept="image/*"
                />
                <GlassButton 
                  onClick={() => document.getElementById('file-upload').click()} 
                  className="cursor-pointer"
                >
                  Browse Files
                </GlassButton>
              </>
            )}

            <AnimatePresence>
              {selectedFile && !result && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 10 }}
                  className="mt-12 flex flex-col items-center"
                >
                  <GlassButton 
                    onClick={handleUpload} 
                    className="min-w-[200px]"
                    variant="primary"
                  >
                    {uploading ? (
                      <div className="flex items-center gap-2">
                        <Loader2 className="animate-spin" />
                        Analyzing...
                      </div>
                    ) : (
                      <div className="flex items-center gap-2">
                        <Sparkles size={18} />
                        Run AI Diagnostic
                      </div>
                    )}
                  </GlassButton>
                  <p className="mt-4 text-xs font-bold uppercase tracking-widest text-teal-900/30 dark:text-white/30">
                    Powered by Quantum Intelligence
                  </p>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </GlassCard>

        {/* Prediction Results */}
        <AnimatePresence>
          {result && <ResultCard result={result} />}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default Dashboard;
