import React, { useRef } from 'react';
import { motion } from 'framer-motion';
import { ArrowRight, ShieldCheck, Zap, BarChart3, Microscope, UserPlus, Upload, Cpu, Database } from 'lucide-react';
import GlassCard from '../components/GlassCard';
import GlassButton from '../components/GlassButton';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const LandingPage = () => {
  const { user } = useAuth();
  const guideRef = useRef(null);

  const scrollToGuide = () => {
    guideRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  const features = [
    {
      icon: <Microscope className="text-accentGradientStart" />,
      title: "Quantum AI Analysis",
      description: "Harnessing hybrid quantum-classical models for unprecedented accuracy in disease detection."
    },
    {
      icon: <Zap className="text-yellow-500" />,
      title: "Real-time Detection",
      description: "Get instant results within seconds of uploading a leaf image, enabling immediate action."
    },
    {
      icon: <ShieldCheck className="text-blue-500" />,
      title: "Early Prevention",
      description: "Detect diseases at their earliest stages before they spread across your entire crop."
    },
    {
      icon: <BarChart3 className="text-purple-500" />,
      title: "Historical Insights",
      description: "Track and analyze your crop health trends with our comprehensive scanning history page."
    }
  ];

  return (
    <div className="space-y-24">
      {/* Hero Section */}
      <section className="text-center space-y-8 relative">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8 }}
          className="inline-block px-4 py-1.5 rounded-full bg-white/30 dark:bg-black/30 backdrop-blur-md border border-white/20 text-teal-800 dark:text-accentGradientStart text-sm font-medium mb-4"
        >
          ✨ The Future of Agriculture is Here
        </motion.div>
        
        <motion.h1
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="text-5xl md:text-7xl font-black leading-tight"
        >
          Q-Powered Crop <br />
          <span className="bg-gradient-to-r from-accentGradientStart to-accentGradientEnd bg-clip-text text-transparent">
            Disease Detection
          </span>
        </motion.h1>
        
        <motion.p
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
          className="text-lg md:text-xl text-teal-900/60 dark:text-white/60 max-w-2xl mx-auto"
        >
          Protect your harvest with hybrid quantum intelligence. Upload a photo and let our advanced neural networks identify plant health issues in seconds.
        </motion.p>
        
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.6 }}
          className="flex flex-wrap justify-center gap-4 pt-4"
        >
          <Link to="/dashboard">
            <GlassButton className="px-10 py-5 text-lg">
              Start Scanning <ArrowRight size={20} />
            </GlassButton>
          </Link>
          <GlassButton variant="secondary" className="px-10 py-5 text-lg" onClick={scrollToGuide}>
            Learn More
          </GlassButton>
        </motion.div>

        {/* Floating elements for visual interest */}
        <motion.div 
          animate={{ y: [0, -20, 0] }}
          transition={{ duration: 5, repeat: Infinity, ease: "easeInOut" }}
          className="absolute -top-10 -right-20 w-32 h-32 bg-accentGradientStart opacity-10 blur-3xl rounded-full"
        ></motion.div>
        <motion.div 
          animate={{ y: [0, 20, 0] }}
          transition={{ duration: 6, repeat: Infinity, ease: "easeInOut" }}
          className="absolute top-40 -left-20 w-40 h-40 bg-accentGradientEnd opacity-10 blur-3xl rounded-full"
        ></motion.div>
      </section>

      {/* Features Grid */}
      <section className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
        {features.map((feature, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 * index }}
          >
            <GlassCard className="h-full flex flex-col items-center text-center group">
              <div className="w-14 h-14 rounded-2xl bg-white/50 dark:bg-black/50 flex items-center justify-center mb-6 group-hover:scale-110 group-hover:rotate-6 transition-transform duration-300">
                {feature.icon}
              </div>
              <h3 className="text-xl font-bold mb-3">{feature.title}</h3>
              <p className="text-teal-900/60 dark:text-white/60 text-sm leading-relaxed">
                {feature.description}
              </p>
            </GlassCard>
          </motion.div>
        ))}
      </section>

      {/* How It Works Guide */}
      <section ref={guideRef} className="py-24 space-y-16">
        <div className="text-center space-y-4">
          <h2 className="text-4xl font-black">How It Works</h2>
          <p className="text-teal-900/60 dark:text-white/60 max-w-xl mx-auto font-medium">
            Unlock the power of AgriLens in four simple steps. Designed for precision, built for efficiency.
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8 relative">
          {/* Connecting Line (Desktop) */}
          <div className="hidden lg:block absolute top-1/2 left-0 w-full h-0.5 bg-white/20 dark:bg-white/5 -translate-y-1/2 z-0"></div>
          
          {[
            {
              icon: <UserPlus className="text-blue-500" />,
              title: "1. Join the Network",
              description: "Create your AgriLens account to access advanced quantum diagnostics and personalized tracking."
            },
            {
              icon: <Upload className="text-accentGradientStart" />,
              title: "2. Capture & Upload",
              description: "Take a clear photo of the plant leaf and upload it to our secure dashboard for analysis."
            },
            {
              icon: <Cpu className="text-purple-500" />,
              title: "3. Quantum Analysis",
              description: "Our hybrid neural networks identify cellular patterns for precise disease identification."
            },
            {
              icon: <Database className="text-yellow-500" />,
              title: "4. Manage Health",
              description: "Review detailed results and track historical data in your personalized scan history."
            }
          ].map((step, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, scale: 0.9 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className="relative z-10"
            >
              <GlassCard className="h-full !p-8 flex flex-col items-center text-center hover:bg-white/40 group">
                <div className="w-16 h-16 rounded-2xl bg-white/50 dark:bg-black/50 flex items-center justify-center mb-6 shadow-lg group-hover:accent-gradient group-hover:text-white transition-all duration-500">
                  {step.icon}
                </div>
                <h3 className="text-xl font-black mb-3">{step.title}</h3>
                <p className="text-teal-900/60 dark:text-white/60 text-sm leading-relaxed font-medium">
                  {step.description}
                </p>
              </GlassCard>
            </motion.div>
          ))}
        </div>

        <div className="mt-12 flex justify-center">
            <Link to={user ? "/dashboard" : "/login"}>
                <GlassButton className="px-12">
                   Get Started Now
                </GlassButton>
            </Link>
        </div>
      </section>

      {/* Trust Section */}
      <section className="text-center py-12">
        <h2 className="text-3xl font-bold mb-12">Trusted by Modern Farmers</h2>
        <div className="flex flex-wrap justify-center gap-12 opacity-40 grayscale hover:grayscale-0 transition-all duration-700">
          <div className="text-2xl font-black italic">AGRI-TECH</div>
          <div className="text-2xl font-black italic">BIO-GROW</div>
          <div className="text-2xl font-black italic">EARTH-SENSE</div>
          <div className="text-2xl font-black italic">GREEN-PATH</div>
          <div className="text-2xl font-black italic">NATURE-MAX</div>
        </div>
      </section>
    </div>
  );
};

export default LandingPage;
