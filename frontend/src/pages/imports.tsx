/**
 * Data Import Page - CSV Upload and Import Management
 */
import { useState, useEffect } from 'react';
import Head from 'next/head';
import AuthGuard from '../components/AuthGuard';
import Navigation from '../components/Navigation';
import api from '../services/api';

interface Geography {
  id: number;
  name: string;
  state_code: string;
}

interface IngestionRun {
  id: string;
  geography_id: number;
  source_type: string;
  status: string;
  records_upserted: number | null;
  error_message: string | null;
  created_at: string;
  started_at: string | null;
  finished_at: string | null;
}

export default function ImportsPage() {
  const [geographies, setGeographies] = useState<Geography[]>([]);
  const [selectedGeography, setSelectedGeography] = useState<number | null>(null);
  const [importType, setImportType] = useState<'property' | 'events' | 'channels'>('property');
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [importing, setImporting] = useState(false);
  const [ingestionRuns, setIngestionRuns] = useState<IngestionRun[]>([]);
  const [fileRef, setFileRef] = useState<string | null>(null);

  useEffect(() => {
    fetchGeographies();
    fetchIngestionRuns();
  }, []);

  const fetchGeographies = async () => {
    try {
      const response = await api.get('/api/v1/geography/');
      setGeographies(response.data);
    } catch (error) {
      console.error('Failed to fetch geographies:', error);
    }
  };

  const fetchIngestionRuns = async () => {
    try {
      const response = await api.get('/api/v1/ingestion-runs/');
      setIngestionRuns(response.data);
    } catch (error) {
      console.error('Failed to fetch ingestion runs:', error);
    }
  };

  const handleFileUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file || !selectedGeography) return;

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await api.post('/api/v1/uploads/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setFileRef(response.data.file_ref);
      alert('File uploaded successfully');
    } catch (error: any) {
      alert(error.response?.data?.detail || 'File upload failed');
    } finally {
      setUploading(false);
    }
  };

  const handleImport = async () => {
    if (!fileRef || !selectedGeography) return;

    setImporting(true);
    try {
      await api.post(`/api/v1/import/${importType}`, null, {
        params: {
          geography_id: selectedGeography,
          file_ref: fileRef,
        },
      });
      alert('Import started successfully');
      fetchIngestionRuns();
      setFileRef(null);
      setFile(null);
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Import failed');
    } finally {
      setImporting(false);
    }
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleString();
  };

  return (
    <AuthGuard>
      <div className="min-h-screen bg-gray-50">
        <Head>
          <title>Data Import - Local Buyer Intelligence Platform</title>
        </Head>

        <Navigation />

        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="mb-6">
            <h1 className="text-3xl font-bold text-gray-900">Data Import</h1>
            <p className="mt-1 text-sm text-gray-500">
              Upload and import CSV files for property, events, or channels data
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Upload Form */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-bold mb-4">Upload CSV File</h2>
              
              <form onSubmit={handleFileUpload} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Geography
                  </label>
                  <select
                    required
                    value={selectedGeography || ''}
                    onChange={(e) => setSelectedGeography(parseInt(e.target.value))}
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                  >
                    <option value="">Select geography...</option>
                    {geographies.map((geo) => (
                      <option key={geo.id} value={geo.id}>
                        {geo.name}, {geo.state_code}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Import Type
                  </label>
                  <select
                    value={importType}
                    onChange={(e) => setImportType(e.target.value as any)}
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                  >
                    <option value="property">Property Data</option>
                    <option value="events">Events Data</option>
                    <option value="channels">Channels Data</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    CSV File
                  </label>
                  <input
                    type="file"
                    accept=".csv,.txt"
                    required
                    onChange={(e) => setFile(e.target.files?.[0] || null)}
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                  />
                  <p className="mt-1 text-xs text-gray-500">
                    See examples/ folder for CSV templates
                  </p>
                </div>

                <button
                  type="submit"
                  disabled={uploading}
                  className="w-full bg-primary-600 text-white py-2 px-4 rounded-md hover:bg-primary-700 disabled:bg-gray-400"
                >
                  {uploading ? 'Uploading...' : 'Upload File'}
                </button>

                {fileRef && (
                  <button
                    type="button"
                    onClick={handleImport}
                    disabled={importing}
                    className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 disabled:bg-gray-400"
                  >
                    {importing ? 'Starting Import...' : 'Start Import'}
                  </button>
                )}
              </form>
            </div>

            {/* Import History */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-bold mb-4">Import History</h2>
              
              <div className="space-y-4 max-h-96 overflow-y-auto">
                {ingestionRuns.length === 0 ? (
                  <p className="text-gray-500 text-sm">No imports yet</p>
                ) : (
                  ingestionRuns.map((run) => (
                    <div
                      key={run.id}
                      className="border border-gray-200 rounded-md p-4"
                    >
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <div className="font-medium">{run.source_type}</div>
                          <div className="text-sm text-gray-500">
                            Geography ID: {run.geography_id}
                          </div>
                        </div>
                        <span
                          className={`px-2 py-1 text-xs rounded ${
                            run.status === 'success'
                              ? 'bg-green-100 text-green-800'
                              : run.status === 'failed'
                              ? 'bg-red-100 text-red-800'
                              : run.status === 'running'
                              ? 'bg-blue-100 text-blue-800'
                              : 'bg-gray-100 text-gray-800'
                          }`}
                        >
                          {run.status}
                        </span>
                      </div>
                      {run.records_upserted !== null && (
                        <div className="text-sm text-gray-600">
                          Records: {run.records_upserted}
                        </div>
                      )}
                      {run.error_message && (
                        <div className="text-sm text-red-600 mt-1">
                          Error: {run.error_message}
                        </div>
                      )}
                      <div className="text-xs text-gray-400 mt-2">
                        Created: {formatDate(run.created_at)}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </main>
      </div>
    </AuthGuard>
  );
}

