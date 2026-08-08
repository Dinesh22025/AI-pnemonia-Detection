import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { useRouter } from 'next/router';
import toast from 'react-hot-toast';

import { predictionAPI, reportAPI } from '@/services/api';

export default function ReportsPage() {
  const router = useRouter();
  const { id } = router.query;

  const [predictions, setPredictions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!router.isReady) return;
    if (id) {
      // Load a single prediction report
      loadPrediction(String(id));
    } else {
      // Load all predictions for reports listing
      loadPredictions();
    }
  }, [router.isReady, id]);

  const loadPredictions = async () => {
    setLoading(true);
    try {
      const res = await predictionAPI.getHistory(1, 50);
      setPredictions(res.data.predictions);
    } catch (err) {
      console.error('Reports load error:', err);
      toast.error('Failed to load reports');
    } finally {
      setLoading(false);
    }
  };

  const loadPrediction = async (predictionId: string) => {
    setLoading(true);
    try {
      const res = await predictionAPI.getPrediction(predictionId);
      setSelected(res.data);
    } catch (err) {
      setError('Report not found');
      toast.error('Report not found');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async (predictionId: string) => {
    try {
      const res = await reportAPI.download(predictionId);
      const blob = new Blob([res.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `pneumovision_report_${predictionId}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      toast.success('Report downloaded');
    } catch (err: any) {
      const message =
        err?.response?.data?.detail || 'Failed to download report. Please re-generate the report.';
      toast.error(message);
    }
  };

  const handleView = async (predictionId: string) => {
    try {
      const res = await reportAPI.download(predictionId);
      const blob = new Blob([res.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      window.open(url, '_blank');
    } catch (err: any) {
      const message =
        err?.response?.data?.detail || 'Failed to open report. Please re-generate the report.';
      toast.error(message);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500" />
      </div>
    );
  }

  // Single report view
  if (id && selected) {
    return (
      <div className="max-w-4xl mx-auto space-y-8">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Prediction Report</h1>
          <p className="text-gray-500 dark:text-gray-400">Download or view your AI analysis report</p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="card"
        >
          <div className={`text-4xl mb-4 ${selected.prediction === 'Normal' ? 'text-success' : 'text-danger'}`}>
            {selected.prediction === 'Normal' ? '✅' : '⚠️'}
          </div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-1">
            {selected.prediction}
          </h2>
          <p className="text-gray-500 dark:text-gray-400 mb-6">
            Confidence: {(selected.confidence * 100).toFixed(1)}%
          </p>

          <div className="flex flex-wrap gap-4">
            <button onClick={() => handleDownload(selected.id)} className="btn-primary inline-flex">
              📥 Download Report
            </button>
            <button onClick={() => handleView(selected.id)} className="btn-secondary">
              👁️ View Report
            </button>
            <a
              href="/reports"
              className="inline-flex items-center px-5 py-3 rounded-xl border border-gray-200 dark:border-gray-600 text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
            >
              ← Back to Reports
            </a>
          </div>
        </motion.div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto card text-center py-16">
        <p className="text-5xl mb-4">📄</p>
        <p className="text-xl text-gray-500 dark:text-gray-400 mb-4">{error}</p>
        <a href="/reports" className="btn-primary inline-flex">Back to Reports</a>
      </div>
    );
  }

  // Reports listing
  return (
    <div className="space-y-8">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Reports</h1>
        <p className="text-gray-500 dark:text-gray-400">View and download your AI analysis reports</p>
      </motion.div>

      {predictions.length === 0 ? (
        <div className="card text-center py-16">
          <p className="text-5xl mb-4">📄</p>
          <p className="text-xl text-gray-500 dark:text-gray-400 mb-4">No reports available yet</p>
          <a href="/predict" className="btn-primary inline-flex">Upload X-Ray</a>
        </div>
      ) : (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="card p-0 overflow-hidden"
        >
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="text-left text-sm text-gray-500 dark:text-gray-400 border-b border-gray-100 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50">
                  <th className="p-4 font-medium">Date</th>
                  <th className="p-4 font-medium">Result</th>
                  <th className="p-4 font-medium">Confidence</th>
                  <th className="p-4 text-right font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {predictions.map((pred: any) => (
                  <tr key={pred.id} className="border-b border-gray-50 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800/30 transition-colors">
                    <td className="p-4 text-sm text-gray-600 dark:text-gray-400 whitespace-nowrap">
                      {new Date(pred.created_at).toLocaleDateString()}
                    </td>
                    <td className="p-4">
                      <span className={`badge ${pred.prediction === 'Normal' ? 'badge-success' : 'badge-danger'}`}>
                        {pred.prediction}
                      </span>
                    </td>
                    <td className="p-4 font-semibold text-gray-900 dark:text-white">
                      {(pred.confidence * 100).toFixed(1)}%
                    </td>
                    <td className="p-4">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => handleView(pred.id)}
                          className="px-4 py-2 text-sm text-primary-500 border border-primary-200 dark:border-primary-800 rounded-lg hover:bg-primary-50 dark:hover:bg-primary-900/20 transition-colors"
                        >
                          View
                        </button>
                        <button
                          onClick={() => handleDownload(pred.id)}
                          className="px-4 py-2 text-sm btn-primary"
                        >
                          Download
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </motion.div>
      )}
    </div>
  );
}
