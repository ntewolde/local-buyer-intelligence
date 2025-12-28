/**
 * Reports Page - Generate and Export Intelligence Reports
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

interface Report {
  id: number;
  geography_id: number;
  service_category: string;
  report_name: string | null;
  generated_at: string;
  total_households: number | null;
  target_households: number | null;
  average_demand_score: number | null;
  buyer_profile: any;
  zip_demand_scores: any;
  channel_recommendations: any;
  timing_recommendations: any;
}

export default function ReportsPage() {
  const [geographies, setGeographies] = useState<Geography[]>([]);
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [formData, setFormData] = useState({
    geography_id: '',
    zip_codes: '',
    service_category: 'general',
    report_name: '',
  });

  useEffect(() => {
    fetchGeographies();
    fetchReports();
  }, []);

  const fetchGeographies = async () => {
    try {
      const response = await api.get('/api/v1/geography/');
      setGeographies(response.data);
    } catch (error) {
      console.error('Failed to fetch geographies:', error);
    }
  };

  const fetchReports = async () => {
    try {
      const response = await api.get('/api/v1/intelligence/reports');
      setReports(response.data);
    } catch (error) {
      console.error('Failed to fetch reports:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    setGenerating(true);

    try {
      await api.post('/api/v1/intelligence/reports', {
        geography_id: parseInt(formData.geography_id),
        zip_codes: formData.zip_codes,
        service_category: formData.service_category,
        report_name: formData.report_name || undefined,
      });
      alert('Report generated successfully');
      fetchReports();
      setFormData({
        geography_id: '',
        zip_codes: '',
        service_category: 'general',
        report_name: '',
      });
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to generate report');
    } finally {
      setGenerating(false);
    }
  };

  const handleExportJSON = (report: Report) => {
    const dataStr = JSON.stringify(report, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `report-${report.id}-${report.service_category}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const handleExportCSV = (report: Report) => {
    // Export ZIP demand scores as CSV
    if (!report.zip_demand_scores) return;

    const rows = Object.entries(report.zip_demand_scores).map(([zip, score]) => [
      zip,
      score,
    ]);

    const csvContent = [
      ['ZIP Code', 'Demand Score'],
      ...rows,
    ]
      .map((row) => row.map((cell) => `"${cell}"`).join(','))
      .join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `report-${report.id}-zip-scores.csv`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const SERVICE_CATEGORIES = [
    { value: 'lawn_care', label: 'Lawn Care' },
    { value: 'security', label: 'Security' },
    { value: 'it_services', label: 'IT Services' },
    { value: 'fireworks', label: 'Fireworks' },
    { value: 'general', label: 'General' },
  ];

  return (
    <AuthGuard>
      <div className="min-h-screen bg-gray-50">
        <Head>
          <title>Reports - Local Buyer Intelligence Platform</title>
        </Head>

        <Navigation />

        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="mb-6">
            <h1 className="text-3xl font-bold text-gray-900">Intelligence Reports</h1>
            <p className="mt-1 text-sm text-gray-500">
              Generate and export buyer intelligence reports
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Report Generator */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-bold mb-4">Generate New Report</h2>
              <form onSubmit={handleGenerate} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Geography *
                  </label>
                  <select
                    required
                    value={formData.geography_id}
                    onChange={(e) => setFormData({ ...formData, geography_id: e.target.value })}
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
                    ZIP Codes (comma-separated) *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.zip_codes}
                    onChange={(e) => setFormData({ ...formData, zip_codes: e.target.value })}
                    placeholder="12345, 12346, 12347"
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Service Category *
                  </label>
                  <select
                    required
                    value={formData.service_category}
                    onChange={(e) => setFormData({ ...formData, service_category: e.target.value })}
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                  >
                    {SERVICE_CATEGORIES.map((cat) => (
                      <option key={cat.value} value={cat.value}>
                        {cat.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Report Name (optional)
                  </label>
                  <input
                    type="text"
                    value={formData.report_name}
                    onChange={(e) => setFormData({ ...formData, report_name: e.target.value })}
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                  />
                </div>

                <button
                  type="submit"
                  disabled={generating}
                  className="w-full bg-primary-600 text-white py-2 px-4 rounded-md hover:bg-primary-700 disabled:bg-gray-400"
                >
                  {generating ? 'Generating...' : 'Generate Report'}
                </button>
              </form>
            </div>

            {/* Report List */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-bold mb-4">Recent Reports</h2>
              
              {loading ? (
                <div className="text-center py-12">Loading...</div>
              ) : reports.length === 0 ? (
                <p className="text-gray-500 text-sm">No reports yet</p>
              ) : (
                <div className="space-y-4 max-h-96 overflow-y-auto">
                  {reports.map((report) => (
                    <div key={report.id} className="border border-gray-200 rounded-md p-4">
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <div className="font-medium">
                            {report.report_name || `${report.service_category} Report`}
                          </div>
                          <div className="text-sm text-gray-500">
                            Geography ID: {report.geography_id} | {report.service_category}
                          </div>
                        </div>
                      </div>
                      
                      {report.total_households !== null && (
                        <div className="text-sm text-gray-600 mb-2">
                          Households: {report.total_households.toLocaleString()} | 
                          Score: {report.average_demand_score?.toFixed(2) || 'N/A'}
                        </div>
                      )}

                      <div className="flex space-x-2 mt-3">
                        <button
                          onClick={() => handleExportJSON(report)}
                          className="text-sm bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700"
                        >
                          Export JSON
                        </button>
                        <button
                          onClick={() => handleExportCSV(report)}
                          className="text-sm bg-green-600 text-white px-3 py-1 rounded hover:bg-green-700"
                        >
                          Export CSV
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </main>
      </div>
    </AuthGuard>
  );
}






