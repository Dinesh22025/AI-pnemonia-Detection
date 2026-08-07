import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import Link from 'next/link';
import toast from 'react-hot-toast';

import { predictionAPI } from '@/services/api';

export default function HistoryPage() {
  const [predictions, setPredictions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const pageSize = 10;

  useEffect(() => {
    loadHistory();
  }, [page]);

  const loadHistory = async () => {
    setLoading(true);
    try {
      const res = await predictionAPI.getHistory(page, pageSize);
      setPredictions(res.data.predictions);
      setTotal(res.data.total);
    } catch (err) {
      console.error('History load error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this prediction?')) return;
    try {
      await predictionAPI.deletePrediction(id);
      setPredictions(predictions.filter((p) => p.id !== id));
      toast.success('Prediction deleted');
    } catch (err) {
      toast.error('Delete failed');
    }
  };

  const totalPages = Math.ceil(total / pageSize);

  return (
    <div className="space-y-8">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Prediction History</h1>
        <p className="text-gray-500 dark:text-gray-400">View all your chest X-ray analyses</p>
      </motion.div>

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500" />
        </div>
      ) : predictions.length === 0 ? (
        <div className="card text-center py-16">
          <p className="text-5xl mb-4">📋</p>
          <p className="text-xl text-gray-500 dark:text-gray-400 mb-4">No predictions yet</p>
          <Link href="/predict" className="btn-primary inline-flex">Upload X-Ray</Link>
        </div>
      ) : (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card p-0 overflow-hidden"
        >
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="text-left text-sm text-gray-500 dark:text-gray-400 border-b border-gray-100 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50">
                  <th className="p-4 font-medium">Date</th>
                  <th className="p-4 font-medium">Image</th>
                  <th className="p-4 font-medium">Result</th>
                  <th className="p-4 font-medium">Confidence</th>
                  <th className="p-4 font-medium">Normal</th>
                  <th className="p-4 font-medium">Pneumonia</th>
                  <th className="p-4 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {predictions.map((pred: any) => (
                  <tr key={pred.id} className="border-b border-gray-50 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800/30 transition-colors">
                    <td className="p-4 text-sm text-gray-600 dark:text-gray-400 whitespace-nowrap">
                      {new Date(pred.created_at).toLocaleDateString()}
                    </td>
                    <td className="p-4">
                      <img
                        src={`http://localhost:8000/${pred.image_path.replace(/\\/g, '/')}`}
                        alt="X-Ray"
                        className="w-12 h-12 object-cover rounded-lg"
                      />
                    </td>
                    <td className="p-4">
                      <span className={`badge ${pred.prediction === 'Normal' ? 'badge-success' : 'badge-danger'}`}>
                        {pred.prediction}
                      </span>
                    </td>
                    <td className="p-4 font-semibold text-gray-900 dark:text-white">
                      {(pred.confidence * 100).toFixed(1)}%
                    </td>
                    <td className="p-4 text-gray-600 dark:text-gray-400">
                      {(pred.probability_normal * 100).toFixed(1)}%
                    </td>
                    <td className="p-4 text-gray-600 dark:text-gray-400">
                      {(pred.probability_pneumonia * 100).toFixed(1)}%
                    </td>
                    <td className="p-4">
                      <div className="flex items-center gap-2">
                        <Link
                          href={`/reports?id=${pred.id}`}
                          className="p-2 text-primary-500 hover:bg-primary-50 dark:hover:bg-primary-900/20 rounded-lg transition-colors"
                          title="View Report"
                        >
                          📄
                        </Link>
                        <button
                          onClick={() => handleDelete(pred.id)}
                          className="p-2 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
                          title="Delete"
                        >
                          🗑️
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between p-4 border-t border-gray-100 dark:border-gray-700">
              <p className="text-sm text-gray-500">
                Page {page} of {totalPages} ({total} total)
              </p>
              <div className="flex gap-2">
                <button
                  onClick={() => setPage(Math.max(1, page - 1))}
                  disabled={page === 1}
                  className="px-4 py-2 rounded-lg border border-gray-200 dark:border-gray-600 text-sm disabled:opacity-50 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
                >
                  Previous
                </button>
                <button
                  onClick={() => setPage(Math.min(totalPages, page + 1))}
                  disabled={page === totalPages}
                  className="px-4 py-2 rounded-lg border border-gray-200 dark:border-gray-600 text-sm disabled:opacity-50 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </motion.div>
      )}
    </div>
  );
}

