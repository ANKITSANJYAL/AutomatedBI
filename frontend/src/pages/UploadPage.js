import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, CheckCircle, AlertCircle } from 'lucide-react';
import toast from 'react-hot-toast';
import { uploadFile } from '../services/api';

const UploadPage = () => {
  const navigate = useNavigate();
  const [uploading, setUploading] = useState(false);
  const [uploadedFile, setUploadedFile] = useState(null);

  const onDrop = useCallback(async (acceptedFiles) => {
    const file = acceptedFiles[0];
    if (!file) return;

    // Validate file type
    const allowedTypes = ['text/csv', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel'];
    if (!allowedTypes.includes(file.type) && !file.name.match(/\.(csv|xlsx|xls)$/i)) {
      toast.error('Please upload a CSV or Excel file');
      return;
    }

    // Validate file size (50MB)
    if (file.size > 50 * 1024 * 1024) {
      toast.error('File size must be less than 50MB');
      return;
    }

    setUploading(true);
    setUploadedFile(file);

    try {
      const result = await uploadFile(file);
      toast.success('File uploaded successfully!');
      
      // Navigate to processing page
      navigate(`/processing/${result.dataset_id}`);
    } catch (error) {
      toast.error(error.message || 'Upload failed');
      setUploadedFile(null);
    } finally {
      setUploading(false);
    }
  }, [navigate]);

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls']
    },
    maxFiles: 1,
    multiple: false
  });

  return (
    <div className="max-w-4xl mx-auto">
      {/* Hero Section */}
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          AI-Powered Business Intelligence
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          Upload your data and get professional dashboards with intelligent insights in minutes
        </p>
        
        {/* Features */}
        <div className="grid md:grid-cols-3 gap-6 mb-12">
          <div className="card text-center">
            <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mx-auto mb-4">
              <Upload className="w-6 h-6 text-primary-600" />
            </div>
            <h3 className="font-semibold text-gray-900 mb-2">Smart Upload</h3>
            <p className="text-gray-600 text-sm">Automatic data validation and quality analysis</p>
          </div>
          
          <div className="card text-center">
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-4">
              <CheckCircle className="w-6 h-6 text-green-600" />
            </div>
            <h3 className="font-semibold text-gray-900 mb-2">AI Analysis</h3>
            <p className="text-gray-600 text-sm">Domain recognition and KPI recommendations</p>
          </div>
          
          <div className="card text-center">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-4">
              <FileText className="w-6 h-6 text-blue-600" />
            </div>
            <h3 className="font-semibold text-gray-900 mb-2">Pro Dashboard</h3>
            <p className="text-gray-600 text-sm">Interactive charts with best practice design</p>
          </div>
        </div>
      </div>

      {/* Upload Area */}
      <div className="card max-w-2xl mx-auto">
        <div
          {...getRootProps()}
          className={`
            border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-all duration-200
            ${isDragActive && !isDragReject ? 'border-primary-400 bg-primary-50' : ''}
            ${isDragReject ? 'border-red-400 bg-red-50' : ''}
            ${!isDragActive ? 'border-gray-300 hover:border-primary-400 hover:bg-primary-50' : ''}
            ${uploading ? 'pointer-events-none opacity-50' : ''}
          `}
        >
          <input {...getInputProps()} />
          
          {uploading ? (
            <div className="space-y-4">
              <div className="loading-spinner mx-auto"></div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Uploading...</h3>
                <p className="text-gray-600">Please wait while we process your file</p>
              </div>
            </div>
          ) : uploadedFile ? (
            <div className="space-y-4">
              <CheckCircle className="w-12 h-12 text-green-500 mx-auto" />
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">File Ready</h3>
                <p className="text-gray-600">{uploadedFile.name}</p>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {isDragReject ? (
                <>
                  <AlertCircle className="w-12 h-12 text-red-500 mx-auto" />
                  <div>
                    <h3 className="text-lg font-semibold text-red-900 mb-2">Invalid File Type</h3>
                    <p className="text-red-600">Please upload CSV or Excel files only</p>
                  </div>
                </>
              ) : (
                <>
                  <Upload className="w-12 h-12 text-gray-400 mx-auto" />
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                      {isDragActive ? 'Drop your file here' : 'Upload your data file'}
                    </h3>
                    <p className="text-gray-600 mb-4">
                      Drag & drop your CSV or Excel file, or click to browse
                    </p>
                    <div className="inline-flex items-center space-x-2 text-sm text-gray-500">
                      <span>Supported formats:</span>
                      <span className="bg-gray-100 px-2 py-1 rounded">.csv</span>
                      <span className="bg-gray-100 px-2 py-1 rounded">.xlsx</span>
                      <span className="bg-gray-100 px-2 py-1 rounded">.xls</span>
                    </div>
                  </div>
                </>
              )}
            </div>
          )}
        </div>

        {/* Upload Guidelines */}
        <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
          <h4 className="font-medium text-blue-900 mb-2">Upload Guidelines</h4>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• Maximum file size: 50MB</li>
            <li>• Ensure your data has column headers</li>
            <li>• Clean data produces better insights</li>
            <li>• Processing time depends on file size</li>
          </ul>
        </div>
      </div>

      {/* Trust Indicators */}
      <div className="mt-12 text-center">
        <div className="flex justify-center items-center space-x-8 text-sm text-gray-500">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            <span>Secure Processing</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
            <span>AI-Powered</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-purple-500 rounded-full"></div>
            <span>Production Ready</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UploadPage;
