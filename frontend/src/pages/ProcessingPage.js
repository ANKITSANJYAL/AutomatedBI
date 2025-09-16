import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { CheckCircle, Clock, AlertCircle, ArrowRight, RefreshCw } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';
import { getProcessingProgress, getUploadStatus } from '../services/api';

const ProcessingPage = () => {
  const { datasetId } = useParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState('pending');
  const [progress, setProgress] = useState({ steps: [], progress_percentage: 0 });
  const [datasetInfo, setDatasetInfo] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!datasetId) {
      navigate('/');
      return;
    }

    // Start polling for progress updates
    const pollProgress = async () => {
      try {
        const [progressData, statusData] = await Promise.all([
          getProcessingProgress(datasetId),
          getUploadStatus(datasetId)
        ]);
        
        setProgress(progressData);
        setStatus(statusData.status);
        setDatasetInfo(statusData);
        
        // If completed, navigate to dashboard after a short delay
        if (statusData.status === 'completed') {
          setTimeout(() => {
            navigate(`/dashboard/${datasetId}`);
          }, 2000);
        }
        
        // If failed, show error
        if (statusData.status === 'failed') {
          setError(statusData.error_message || 'Processing failed');
          toast.error('Processing failed. Please try uploading again.');
        }
      } catch (err) {
        setError(err.message);
        toast.error('Failed to get processing status');
      }
    };

    // Initial call
    pollProgress();

    // Set up polling interval
    const interval = setInterval(pollProgress, 2000); // Poll every 2 seconds

    return () => clearInterval(interval);
  }, [datasetId, navigate]);

  const getStepIcon = (step) => {
    switch (step.status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-600" />;
      case 'failed':
        return <AlertCircle className="w-5 h-5 text-red-600" />;
      case 'processing':
        return <RefreshCw className="w-5 h-5 text-blue-600 animate-spin" />;
      default:
        return <Clock className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStepStatus = (step) => {
    switch (step.status) {
      case 'completed':
        return 'status-completed';
      case 'failed':
        return 'status-failed';
      case 'processing':
        return 'status-processing';
      default:
        return 'status-pending';
    }
  };

  if (error) {
    return (
      <div className="max-w-2xl mx-auto text-center">
        <div className="card">
          <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Processing Failed</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <button
            onClick={() => navigate('/')}
            className="btn-primary"
          >
            Upload New File
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Processing Your Data
        </h1>
        <p className="text-gray-600">
          Our AI agents are analyzing your dataset and creating intelligent dashboards
        </p>
        {datasetInfo && (
          <p className="text-sm text-gray-500 mt-2">
            File: {datasetInfo.original_filename}
          </p>
        )}
      </div>

      {/* Progress Overview */}
      <div className="card mb-8">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Overall Progress</h3>
          <span className={`status-badge ${
            status === 'completed' ? 'status-completed' :
            status === 'processing' ? 'status-processing' :
            status === 'failed' ? 'status-failed' : 'status-pending'
          }`}>
            {status === 'completed' ? 'Completed' :
             status === 'processing' ? 'Processing' :
             status === 'failed' ? 'Failed' : 'Pending'}
          </span>
        </div>
        
        <div className="progress-bar mb-2">
          <motion.div
            className="progress-fill"
            initial={{ width: 0 }}
            animate={{ width: `${progress.progress_percentage || 0}%` }}
            transition={{ duration: 0.5 }}
          />
        </div>
        
        <div className="text-sm text-gray-600 text-right">
          {Math.round(progress.progress_percentage || 0)}% complete
        </div>
      </div>

      {/* Processing Steps */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-6">Processing Steps</h3>
        
        <div className="space-y-4">
          <AnimatePresence>
            {progress.steps.map((step, index) => (
              <motion.div
                key={step.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className={`
                  flex items-center p-4 rounded-lg border-2 transition-all duration-200
                  ${step.status === 'completed' ? 'bg-green-50 border-green-200' :
                    step.status === 'processing' ? 'bg-blue-50 border-blue-200' :
                    step.status === 'failed' ? 'bg-red-50 border-red-200' :
                    'bg-gray-50 border-gray-200'}
                `}
              >
                <div className="flex-shrink-0 mr-4">
                  {getStepIcon(step)}
                </div>
                
                <div className="flex-grow">
                  <h4 className="font-medium text-gray-900">{step.name}</h4>
                  <p className="text-sm text-gray-600">
                    {step.status === 'completed' ? 'Completed successfully' :
                     step.status === 'processing' ? 'Currently processing...' :
                     step.status === 'failed' ? 'Processing failed' :
                     'Waiting to start'}
                  </p>
                </div>
                
                <div className="flex-shrink-0">
                  <span className={`status-badge ${getStepStatus(step)}`}>
                    {step.status}
                  </span>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      </div>

      {/* AI Analysis Info */}
      <div className="mt-8 grid md:grid-cols-2 gap-6">
        <div className="card">
          <h4 className="font-semibold text-gray-900 mb-3">What's Happening?</h4>
          <ul className="space-y-2 text-sm text-gray-600">
            <li>• Analyzing data quality and structure</li>
            <li>• Identifying business domain and context</li>
            <li>• Recommending relevant KPIs and metrics</li>
            <li>• Designing optimal dashboard layout</li>
            <li>• Generating interactive visualizations</li>
          </ul>
        </div>
        
        <div className="card">
          <h4 className="font-semibold text-gray-900 mb-3">AI Technologies</h4>
          <div className="space-y-3">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                <span className="text-blue-600 font-semibold text-xs">AI</span>
              </div>
              <div>
                <p className="font-medium text-gray-900">CrewAI Agents</p>
                <p className="text-xs text-gray-600">Multi-agent analysis system</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
                <span className="text-green-600 font-semibold text-xs">GM</span>
              </div>
              <div>
                <p className="font-medium text-gray-900">Gemini AI</p>
                <p className="text-xs text-gray-600">Advanced language model</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Auto-redirect notification */}
      {status === 'completed' && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="mt-8 card bg-green-50 border-green-200"
        >
          <div className="flex items-center space-x-3">
            <CheckCircle className="w-6 h-6 text-green-600" />
            <div className="flex-grow">
              <h4 className="font-semibold text-green-900">Processing Complete!</h4>
              <p className="text-green-700">Redirecting to your dashboard...</p>
            </div>
            <ArrowRight className="w-5 h-5 text-green-600 animate-pulse" />
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default ProcessingPage;
