import os

file_path = r'c:\Users\Dinesh\OneDrive\Desktop\PneumoVisionAI\frontend\pages\predict.tsx'

code = r'''import React, { useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { useDropzone } from 'react-dropzone';
import toast from 'react-hot-toast';

import { useAppDispatch, setUploading, addPrediction } from '@/services/store';
import { predictionAPI } from '@/services/api';

export default function PredictPage() {
  const dispatch = useAppDispatch();
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    const validTypes = ['image/png', 'image/jpeg', 'image/jpg'];
    if (!validTypes.includes(file.type)) {
      toast.error('Please upload a PNG, JPG, or JPEG image');
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      toast.error('File size must be less than 10MB');
      return;
    }

    setUploadedFile(file);
    setPreview(URL.createObjectURL(file));
    setResult(null);
    setError(null);

    setIsUploading(true);
    dispatch(setUploading(true));
    try {
      const res = await predictionAPI.upload(file);
      setResult(res.data);
      dispatch(addPrediction(res.data));
      toast.success('Analysis complete!');
    } catch (err: any) {
      const message = err.response?.data?.detail || 'Upload failed. Make sure the backend server is running.';
      setError(message);
      toast.error(message);
    } finally {
      setIsUploading(false);
      dispatch(setUploading(false));
    }
  }, [dispatch]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'image/*': ['.png', '.jpg', '.jpeg'] },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024,
  });

  const handleDownloadReport = async () => {
    if (!result?.id) return;
    try {
      const reportRes = await fetch('http://localhost:8000/reports/' + result.id);
      const blob = await reportRes.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'pneumovision_report_' + result.id + '.pdf';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      toast.success('Report downloaded');
    } catch (err) {
      toast.error('Download failed');
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">X-Ray Analysis</h1>
        <p className="text-gray-500 dark:text-gray-400">
          Upload a chest X-ray image for AI-powered pneumonia detection
        </p>
      </motion.div>

      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
        <div
          {...getRootProps()}
          className={
            'relative border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all duration-300 ' +
            (isDragActive
              ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
              : 'border-gray-300 dark:border-gray-600 hover:border-primary-400 hover:bg-gray-50 dark:hover:bg-gray-800/50'
            )
          }
        >
          <input {...getInputProps()} />
          {preview ? (
            <div className="relative">
              <img src={preview} alt="X-Ray Preview" className="max-h-80 mx-auto rounded-xl shadow-lg" />
              {isUploading && (
                <div className="absolute inset-0 bg-black/40 rounded-xl flex items-center justify-center">
                  <div className="text-white text-center">
                    <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-white mx-auto mb-2"></div>
                    <p>Analyzing...</p>
                  </div>
              )}
            </div>
          ) : (
            <div>
              <div className="text-6xl mb-4">{isDragActive ? '\U0001F4C2' : '\U0001F4E4'}</div>
              <p className="text-xl font-semibold text-gray-700 dark:text-gray-300 mb-2">
                {isDragActive ? 'Drop your X-Ray here' : 'Drag and drop chest X-ray'}
              </p>
              <p className="text-gray-500 dark:text-gray-400 mb-4">or click to browse</p>
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-gray-100 dark:bg-gray-700 rounded-lg text-sm text-gray-500 dark:text-gray-400">
                <span>PNG, JPG, JPEG</span>
                <span>|</span>
                <span>Max 10MB</span>
              </div>

        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500 mx-auto"></div>
          <p className="text-gray-500 mt-2">Analyzing your X-ray...</p>
        </div>
      )}

      {result && (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
          <div
            className={
              'card text-center ' +
              (result.prediction === 'Normal'
                ? 'border-green-200 dark:border-green-800'
                : 'border-red-200 dark:border-red-800'
              )
            }
          >
            <div className="text-5xl mb-4">{result.prediction === 'Normal' ? '\u2705' : '\u26A0\uFE0F'}</div>
            <h2
              className={
                'text-3xl font-bold mb-2 ' +
                (result.prediction === 'Normal' ? 'text-success' : 'text-danger')
              }
            >
              {result.prediction}
            </h2>
            <p className="text-gray-500 dark:text-gray-400 mb-6">
              Detected with {(result.confidence * 100).toFixed(1)}% confidence
            </p>
            <div className="max-w-md mx-auto space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600 dark:text-gray-400">Normal</span>
                  <span className="font-semibold">{(result.probability_normal * 100).toFixed(1)}%</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
                  <div
                    className="bg-success rounded-full h-3 transition-all duration-1000"
                    style={{ width: result.probability_normal * 100 + '%' }}
                  ></div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600 dark:text-gray-400">Pneumonia</span>
                  <span className="font-semibold">{(result.probability_pneumonia * 100).toFixed(1)}%</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
                  <div
                    className="bg-danger rounded-full h-3 transition-all duration-1000"
                    style={{ width: result.probability_pneumonia * 100 + '%' }}
                  ></div>
              </div>
          </div>

          {result.gradcam_image && (
            <div className="card">
              <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">AI Attention Map (Grad-CAM)</h3>
              <div className="flex justify-center">
                <img
                  src={'http://localhost:8000/' + result.gradcam_image.replace(/\\\\/g, '/')}
                  alt="GradCAM Heatmap"
                  className="max-h-80 rounded-xl shadow-lg"
                />
              </div>
              <p className="text-center text-sm text-gray-500 mt-3">
                Red regions indicate areas the AI focused on for its decision
              </p>
            </div>
          )}

          <div className="flex justify-center gap-4">
            <button onClick={handleDownloadReport} className="btn-primary">
              Download Report
            </button>
            <button
              onClick={() => {
                setResult(null);
                setPreview(null);
                setUploadedFile(null);
              }}
              className="btn-secondary"
            >
              New Analysis
            </button>
          </div>
        </motion.div>
      )}

      {error && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="card bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800"
        >
          <p className="text-red-600 dark:text-red-400">{error}</p>
        </motion.div>
      )}
    </div>
  );
}
'''

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(code)
print('File written successfully')
</｜｜DSML｜｜parameter>
</create_file>
