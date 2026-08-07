import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';

import { useAppSelector } from '@/services/store';
import { predictionAPI } from '@/services/api';

export default function DashboardPage() {
  const { user } = useAppSelector((state: any) => state.auth);
  const [stats, setStats] = useState<any>(null);
  const [recentPredictions, setRecentPredictions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      const [statsRes, historyRes] = await Promise.all([
        predictionAPI.getStats(),
        predictionAPI.getHistory(1, 5),
      ]);
      setStats(statsRes.data);
      setRecentPredictions(historyRes.data.predictions);
    } catch (err) {
      console.error('Dashboard load error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500" />
      </div>
    );
  }

  const cards = [
    {
      title: 'Total Predictions',
      value: stats?.total_predictions || 0,
      icon: '🔬',
      color: 'from-blue-500 to-cyan-500',
      bg: 'bg-blue-50 dark:bg-blue-900/20',
    },
    {
      title: 'Normal Results',
      value: stats?.normal_count || 0,
      icon: '✅',
      color: 'from-green-500 to-emerald-500',
      bg: 'bg-green-50 dark:bg-green-900/20',
    },
    {
      title: 'Pneumonia Detected',
      value: stats?.pneumonia_count || 0,
      icon: '⚠️',
      color: 'from-orange-500 to-red-500',
      bg: 'bg-orange-50 dark:bg-orange-900/20',
    },
    {
      title: 'Avg Confidence',
      value: stats ? `${(stats.average_confidence * 100).toFixed(1)}%` : '0%',
      icon: '🎯',
      color: 'from-purple-500 to-pink-500',
      bg: 'bg-purple-50 dark:bg-purple-900/20',
    },
  ];

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-card p-8 bg-gradient-to-r from-primary-500 to-accent-500 text-white"
      >
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">
              Welcome back, {user?.name?.split(' ')[0] || 'User'}! 👋
            </h1>
            <p className="text-white/80 text-lg">
              {stats?.total_predictions > 0
                ? `You've performed ${stats.total_predictions} predictions so far.`
                : 'Ready to analyze your first chest X-ray?'}
            </p>
          </div>
          <Link href="/predict" className="hidden md:inline-flex items-center gap-2 px-6 py-3 bg-white text-primary-500 font-semibold rounded-xl hover:bg-gray-100 transition-all shadow-lg">
            <span>+</span>
            <span>New Prediction</span>
          </Link>
        </div>
      </motion.div>

      {/* Stats Cards */}
      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {cards.map((card, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className={`card ${card.bg}`}
          >
            <div className="flex items-center justify-between mb-4">
              <span className="text-3xl">{card.icon}</span>
              <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${card.color} opacity-20`} />
            </div>
            <p className="text-3xl font-bold text-gray-900 dark:text-white mb-1">{card.value}</p>
            <p className="text-sm text-gray-500 dark:text-gray-400">{card.title}</p>
          </motion.div>
        ))}
      </div>

      {/* Recent Predictions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="card"
      >
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">Recent Predictions</h2>
          <Link href="/history" className="text-primary-500 hover:text-primary-600 font-medium text-sm">
            View All →
          </Link>
        </div>

        {recentPredictions.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-5xl mb-4">🔬</p>
            <p className="text-gray-500 dark:text-gray-400 mb-4">No predictions yet</p>
            <Link href="/predict" className="btn-primary inline-flex">
              Upload Your First X-Ray
            </Link>
          </div>
        ) : (
          <div className="space-y-4">
            {recentPredictions.map((pred: any) => (
              <Link
                key={pred.id}
                href={`/history?prediction=${pred.id}`}
                className="flex items-center justify-between p-4 rounded-xl bg-gray-50 dark:bg-gray-800/50 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
              >
                <div className="flex items-center gap-4">
                  <div className={`w-12 h-12 rounded-xl flex items-center justify-center text-lg font-bold ${
                    pred.prediction === 'Normal'
                      ? 'bg-green-100 dark:bg-green-900/20 text-green-600'
                      : 'bg-red-100 dark:bg-red-900/20 text-red-600'
                  }`}>
                    {pred.prediction === 'Normal' ? 'N' : 'P'}
                  </div>
                  <div>
                    <p className="font-semibold text-gray-900 dark:text-white">{pred.prediction}</p>
                    <p className="text-sm text-gray-500">
                      Confidence: {(pred.confidence * 100).toFixed(1)}%
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm text-gray-500">
                    {new Date(pred.created_at).toLocaleDateString()}
                  </p>
                </div>
              </Link>
            ))}
          </div>
        )}
      </motion.div>

      {/* Health Tips */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="card"
      >
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">💡 Health Tips</h2>
        <div className="grid md:grid-cols-3 gap-4">
          {[
            {
              tip: 'Regular Check-ups',
              desc: 'Annual chest X-rays recommended for smokers and individuals over 50',
              icon: '🏥',
            },
            {
              tip: 'Know the Symptoms',
              desc: 'Persistent cough, fever, chills, and shortness of breath may indicate pneumonia',
              icon: '🫁',
            },
            {
              tip: 'Stay Vaccinated',
              desc: 'Pneumococcal vaccine can prevent certain types of pneumonia',
              icon: '💉',
            },
          ].map((item, index) => (
            <div key={index} className="p-4 rounded-xl bg-gray-50 dark:bg-gray-800/50">
              <span className="text-2xl mb-2 block">{item.icon}</span>
              <h3 className="font-semibold text-gray-900 dark:text-white mb-1">{item.tip}</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">{item.desc}</p>
            </div>
          ))}
        </div>
      </motion.div>
    </div>
  );
}

