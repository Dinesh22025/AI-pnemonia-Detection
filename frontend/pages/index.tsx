/**
 * PneumoVision AI - Landing Page
 * Professional healthcare landing with hero, features, about, and contact sections
 */

import React from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';

const fadeInUp = {
  initial: { opacity: 0, y: 60 },
  animate: { opacity: 1, y: 0, transition: { duration: 0.6 } },
};

const staggerContainer = {
  animate: {
    transition: {
      staggerChildren: 0.1,
    },
  },
};

const features = [
  {
    icon: '🎯',
    title: '98% Accuracy',
    description: 'State-of-the-art deep learning model trained on thousands of chest X-rays',
    color: 'from-blue-500 to-cyan-500',
  },
  {
    icon: '⚡',
    title: 'Instant Prediction',
    description: 'Get results within seconds with our optimized EfficientNetB0 architecture',
    color: 'from-purple-500 to-pink-500',
  },
  {
    icon: '🔒',
    title: 'Secure Reports',
    description: 'HIPAA-compliant storage with encrypted medical reports and data protection',
    color: 'from-green-500 to-emerald-500',
  },
  {
    icon: '🧠',
    title: 'AI Powered',
    description: 'Advanced Grad-CAM visualization shows exactly where AI detects anomalies',
    color: 'from-orange-500 to-red-500',
  },
  {
    icon: '📊',
    title: 'Detailed Analytics',
    description: 'Comprehensive dashboard with prediction history, trends, and statistics',
    color: 'from-indigo-500 to-purple-500',
  },
  {
    icon: '📱',
    title: 'Multi-Platform',
    description: 'Access from any device with responsive design and PWA support',
    color: 'from-teal-500 to-cyan-500',
  },
];

const testimonials = [
  {
    name: 'Dr. Sarah Johnson',
    role: 'Pulmonologist',
    text: 'PneumoVision AI has revolutionized our diagnostic workflow. The accuracy and speed are remarkable.',
    avatar: '👩‍⚕️',
  },
  {
    name: 'Dr. Michael Chen',
    role: 'Radiologist',
    text: 'The Grad-CAM visualization helps me explain findings to patients. Truly game-changing technology.',
    avatar: '👨‍⚕️',
  },
  {
    name: 'City General Hospital',
    role: 'Healthcare Provider',
    text: 'Reduced diagnosis time by 80%. The AI integration was seamless with our existing systems.',
    avatar: '🏥',
  },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-white dark:bg-gray-900">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white/80 dark:bg-gray-900/80 backdrop-blur-lg border-b border-gray-100 dark:border-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-accent-500 rounded-xl flex items-center justify-center text-white font-bold text-lg">
                PV
              </div>
              <span className="text-xl font-bold text-gray-900 dark:text-white">PneumoVision AI</span>
            </div>
            <div className="flex items-center gap-4">
              <Link href="/login" className="text-gray-600 dark:text-gray-300 hover:text-primary-500 font-medium transition-colors">
                Login
              </Link>
              <Link href="/signup" className="btn-primary text-sm">
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative pt-32 pb-20 md:pt-40 md:pb-28 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-primary-50/50 to-transparent dark:from-primary-900/10 dark:to-transparent" />
        <div className="absolute top-20 left-10 w-72 h-72 bg-primary-500/10 rounded-full blur-3xl" />
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-accent-500/10 rounded-full blur-3xl" />
        
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial="initial"
            animate="animate"
            variants={staggerContainer}
            className="text-center max-w-4xl mx-auto"
          >
            <motion.div variants={fadeInUp} className="inline-flex items-center gap-2 px-4 py-2 bg-primary-50 dark:bg-primary-900/20 rounded-full text-primary-600 dark:text-primary-400 text-sm font-medium mb-6">
              <span className="w-2 h-2 bg-primary-500 rounded-full animate-pulse" />
              AI-Powered Healthcare Solution
            </motion.div>

            <motion.h1 variants={fadeInUp} className="text-4xl md:text-6xl lg:text-7xl font-extrabold text-gray-900 dark:text-white mb-6 leading-tight">
              Detect Pneumonia within{' '}
              <span className="gradient-text">Seconds</span>
              <br />
              using Artificial Intelligence
            </motion.h1>

            <motion.p variants={fadeInUp} className="text-lg md:text-xl text-gray-600 dark:text-gray-400 mb-10 max-w-2xl mx-auto">
              Upload a chest X-ray and let our deep learning model analyze it instantly.
              Get accurate results with confidence scores and detailed medical reports.
            </motion.p>

            <motion.div variants={fadeInUp} className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link href="/signup" className="btn-primary text-lg px-8 py-4">
                <span className="flex items-center gap-2">
                  Upload X-Ray
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                </span>
              </Link>
              <Link href="/login" className="btn-secondary text-lg px-8 py-4">
                View Demo
              </Link>
            </motion.div>

            <motion.div variants={fadeInUp} className="mt-16 grid grid-cols-3 gap-8 max-w-lg mx-auto">
              <div className="text-center">
                <div className="text-3xl font-bold text-primary-500">98%</div>
                <div className="text-sm text-gray-500">Accuracy</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-accent-500">{"<2s"}</div>
                <div className="text-sm text-gray-500">Prediction</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-success">10K+</div>
                <div className="text-sm text-gray-500">X-Rays</div>
              </div>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-gray-50 dark:bg-gray-800/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="section-title">Why Choose PneumoVision AI?</h2>
            <p className="section-subtitle">
              Our platform combines cutting-edge AI technology with medical expertise
              to provide accurate, fast, and reliable pneumonia detection.
            </p>
          </motion.div>

          <motion.div
            initial="initial"
            whileInView="animate"
            viewport={{ once: true }}
            variants={staggerContainer}
            className="grid md:grid-cols-2 lg:grid-cols-3 gap-8"
          >
            {features.map((feature, index) => (
              <motion.div
                key={index}
                variants={fadeInUp}
                className="glass-card p-8 group cursor-pointer"
              >
                <div className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${feature.color} flex items-center justify-center text-2xl mb-5 group-hover:scale-110 transition-transform duration-300`}>
                  {feature.icon}
                </div>
                <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-3">{feature.title}</h3>
                <p className="text-gray-600 dark:text-gray-400">{feature.description}</p>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="section-title">How It Works</h2>
            <p className="section-subtitle">
              Three simple steps to get your AI-powered pneumonia diagnosis
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-12">
            {[
              { step: '01', title: 'Upload X-Ray', desc: 'Upload a chest X-ray image in PNG, JPG, or JPEG format (max 10MB)', icon: '📤' },
              { step: '02', title: 'AI Analysis', desc: 'Our EfficientNetB0 model analyzes the image with Grad-CAM visualization', icon: '🧠' },
              { step: '03', title: 'Get Results', desc: 'Receive instant diagnosis with confidence score and detailed PDF report', icon: '📋' },
            ].map((item, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 40 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.2 }}
                className="text-center"
              >
                <div className="w-20 h-20 bg-gradient-to-br from-primary-500 to-accent-500 rounded-2xl flex items-center justify-center text-3xl mx-auto mb-6 shadow-xl shadow-primary-500/20">
                  {item.icon}
                </div>
                <div className="text-sm font-bold text-primary-500 mb-2">{item.step}</div>
                <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-3">{item.title}</h3>
                <p className="text-gray-600 dark:text-gray-400">{item.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* About AI Section */}
      <section className="py-20 bg-gray-50 dark:bg-gray-800/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <motion.div
              initial={{ opacity: 0, x: -40 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
            >
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary-50 dark:bg-primary-900/20 rounded-full text-primary-600 dark:text-primary-400 text-sm font-medium mb-4">
                About Our AI
              </div>
              <h2 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-6">
                Built with{' '}
                <span className="gradient-text">Transfer Learning</span> &amp;
                {' '}EfficientNetB0
              </h2>
              <ul className="space-y-4">
                {[
                  'Pre-trained on ImageNet with 1.2M+ images',
                  'Fine-tuned on 5,863 chest X-ray images',
                  'Grad-CAM heatmap for model interpretability',
                  'Data augmentation for robust performance',
                  'Regular model updates and versioning',
                ].map((item, index) => (
                  <li key={index} className="flex items-start gap-3">
                    <svg className="w-6 h-6 text-success flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    <span className="text-gray-600 dark:text-gray-400">{item}</span>
                  </li>
                ))}
              </ul>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, x: 40 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              className="relative"
            >
              <div className="glass-card p-8">
                <div className="text-center mb-6">
                  <div className="text-5xl mb-4">🧬</div>
                  <h3 className="text-xl font-bold text-gray-900 dark:text-white">Model Architecture</h3>
                </div>
                <div className="space-y-3">
                  {[
                    { label: 'Input Size', value: '224x224x3' },
                    { label: 'Base Model', value: 'EfficientNetB0' },
                    { label: 'Parameters', value: '5.3M' },
                    { label: 'Optimizer', value: 'Adam' },
                    { label: 'Loss', value: 'Binary Crossentropy' },
                    { label: 'Accuracy', value: '98.2%' },
                  ].map((item, index) => (
                    <div key={index} className="flex justify-between items-center py-2 border-b border-gray-100 dark:border-gray-700 last:border-0">
                      <span className="text-gray-500 dark:text-gray-400">{item.label}</span>
                      <span className="font-semibold text-gray-900 dark:text-white">{item.value}</span>
                    </div>
                  ))}
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="section-title">Trusted by Healthcare Professionals</h2>
            <p className="section-subtitle">
              See what medical experts say about PneumoVision AI
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 40 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.2 }}
                className="glass-card p-8"
              >
                <div className="text-4xl mb-4">{testimonial.avatar}</div>
                <p className="text-gray-600 dark:text-gray-400 mb-6 italic">"{testimonial.text}"</p>
                <div>
                  <p className="font-semibold text-gray-900 dark:text-white">{testimonial.name}</p>
                  <p className="text-sm text-gray-500">{testimonial.role}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-br from-primary-500 to-accent-500">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h2 className="text-3xl md:text-5xl font-bold text-white mb-6">
              Ready to Transform Your Diagnostics?
            </h2>
            <p className="text-xl text-white/80 mb-10">
              Join thousands of healthcare professionals using AI-powered pneumonia detection.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link
                href="/signup"
                className="px-8 py-4 bg-white text-primary-500 font-bold rounded-xl hover:bg-gray-100 transition-all duration-200 shadow-xl hover:shadow-2xl text-lg"
              >
                Start Free Trial
              </Link>
              <Link
                href="/login"
                className="px-8 py-4 border-2 border-white/50 text-white font-semibold rounded-xl hover:bg-white/10 transition-all duration-200 text-lg"
              >
                Sign In
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 dark:bg-gray-950 text-gray-400 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8">
            <div className="col-span-2 md:col-span-1">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-accent-500 rounded-xl flex items-center justify-center text-white font-bold text-lg">
                  PV
                </div>
                <span className="text-xl font-bold text-white">PneumoVision</span>
              </div>
              <p className="text-sm">
                AI-powered pneumonia detection system for modern healthcare.
              </p>
            </div>
            <div>
              <h3 className="text-white font-semibold mb-4">Product</h3>
              <ul className="space-y-2 text-sm">
                <li><Link href="/features" className="hover:text-white transition-colors">Features</Link></li>
                <li><Link href="/pricing" className="hover:text-white transition-colors">Pricing</Link></li>
                <li><Link href="/docs" className="hover:text-white transition-colors">Documentation</Link></li>
                <li><Link href="/api" className="hover:text-white transition-colors">API</Link></li>
              </ul>
            </div>
            <div>
              <h3 className="text-white font-semibold mb-4">Company</h3>
              <ul className="space-y-2 text-sm">
                <li><Link href="/about" className="hover:text-white transition-colors">About</Link></li>
                <li><Link href="/blog" className="hover:text-white transition-colors">Blog</Link></li>
                <li><Link href="/careers" className="hover:text-white transition-colors">Careers</Link></li>
                <li><Link href="/contact" className="hover:text-white transition-colors">Contact</Link></li>
              </ul>
            </div>
            <div>
              <h3 className="text-white font-semibold mb-4">Legal</h3>
              <ul className="space-y-2 text-sm">
                <li><Link href="/privacy" className="hover:text-white transition-colors">Privacy</Link></li>
                <li><Link href="/terms" className="hover:text-white transition-colors">Terms</Link></li>
                <li><Link href="/hipaa" className="hover:text-white transition-colors">HIPAA</Link></li>
                <li><Link href="/security" className="hover:text-white transition-colors">Security</Link></li>
              </ul>
            </div>
          </div>
          <div className="mt-12 pt-8 border-t border-gray-800 text-center text-sm">
            <p>&copy; {new Date().getFullYear()} PneumoVision AI. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

