import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { useAppSelector } from '@/services/store';
import { adminAPI } from '@/services/api';

export default function AdminDashboard() {
  const { user } = useAppSelector((state: any) => state.auth);
  const [stats, setStats] = useState<any>(null);
  const [recentPredictions, setRecentPredictions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAdminData();
  }, []);

  const loadAdminData = async () => {
    try {
      const [statsRes, recentRes] = await Promise.all([
        adminAPI.getStats(),
        adminAPI.getRecentPredictions(10),
      ]);
      setStats(statsRes.data);
      setRecentPredictions(recentRes.data);
    } catch (err) {
      console.error('Admin load error:', err);
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

  const statCards = [
    { label: 'Total Users', value: stats?.total_users || 0, icon: '👥', color: 'from-blue-500 to-cyan-500' },
    { label: 'Total Predictions', value: stats?.total_predictions || 0, icon: '🔬', color: 'from-purple-500 to-pink-500' },
    { label: 'Accuracy', value: `${((stats?.accuracy || 0) * 100).toFixed(1)}%`, icon: '🎯', color: 'from-green-500 to-emerald-500' },
    { label: 'Today', value: stats?.predictions_today || 0, icon: '📊', color: 'from-orange-500 to-red-500' },
  ];

  return (
    <div className="space-y-8">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Admin Dashboard</h1>
        <p className="text-gray-500 dark:text-gray-400">System overview and analytics</p>
      </motion.div>

      {/* Stats Grid */}
      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((card, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="card"
          >
            <div className="flex items-center justify-between mb-4">
              <span className="text-3xl">{card.icon}</span>
              <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${card.color} opacity-20`} />
            </div>
            <p className="text-3xl font-bold text-gray-900 dark:text-white mb-1">{card.value}</p>
            <p className="text-sm text-gray-500">{card.label}</p>
          </motion.div>
        ))}
      </div>

      {/* Distribution */}
      <div className="grid md:grid-cols-2 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="card"
        >
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-6">Prediction Distribution</h2>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-600 dark:text-gray-400">Normal</span>
                <span className="font-semibold">{stats?.normal_count || 0}</span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-4">
                <div
                  className="bg-success rounded-full h-4 transition-all duration-1000"
                  style={{
                    width: `${((stats?.normal_count || 0) / (stats?.total_predictions || 1)) * 100}%`,
                  }}
                />
              </div>
            </div>
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-600 dark:text-gray-400">Pneumonia</span>
                <span className="font-semibold">{stats?.pneumonia_count || 0}</span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-4">
                <div
                  className="bg-danger rounded-full h-4 transition-all duration-1000"
                  style={{
                    width: `${((stats?.pneumonia_count || 0) / (stats?.total_predictions || 1)) * 100}%`,
                  }}
                />
              </div>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="card"
        >
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">System Info</h2>
          <div className="space-y-3">
            {[
              { label: 'Model Version', value: stats?.model_version || '1.0.0' },
              { label: 'Active Users Today', value: stats?.active_users_today || 0 },
              { label: 'Storage Used', value: stats?.storage_used || '0 MB' },
              { label: 'Avg Confidence', value: `${((stats?.average_confidence || 0) * 100).toFixed(1)}%` },
              { label: 'Patients', value: stats?.total_patients || 0 },
              { label: 'Doctors', value: stats?.total_doctors || 0 },
            ].map((item, index) => (
              <div key={index} className="flex justify-between py-2 border-b border-gray-100 dark:border-gray-700 last:border-0">
                <span className="text-gray-500 dark:text-gray-400">{item.label}</span>
                <span className="font-semibold text-gray-900 dark:text-white">{item.value}</span>
              </div>
            ))}
          </div>
        </motion.div>
      </div>

      {/* Recent Predictions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="card"
      >
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-6">Recent Predictions</h2>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="text-left text-sm text-gray-500 dark:text-gray-400 border-b border-gray-100 dark:border-gray-700">
                <th className="pb-3 font-medium">User</th>
                <th className="pb-3 font-medium">Prediction</th>
                <th className="pb-3 font-medium">Confidence</th>
                <th className="pb-3 font-medium">Date</th>
              </tr>
            </thead>
            <tbody>
              {recentPredictions.map((pred: any, index: number) => (
                <tr key={index} className="border-b border-gray-50 dark:border-gray-800">
                  <td className="py-3">
                    <div>
                      <p className="font-medium text-gray-900 dark:text-white">{pred.user_name}</p>
                      <p className="text-sm text-gray-500">{pred.user_email}</p>
                    </div>
                  </td>
                  <td className="py-3">
                    <span className={`badge ${
                      pred.prediction === 'Normal' ? 'badge-success' : 'badge-danger'
                    }`}>
                      {pred.prediction}
                    </span>
                  </td>
                  <td className="py-3 text-gray-900 dark:text-white">
                    {(pred.confidence * 100).toFixed(1)}%
                  </td>
                  <td className="py-3 text-sm text-gray-500">
                    {new Date(pred.created_at).toLocaleDateString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </motion.div>
    </div>
  );
}

