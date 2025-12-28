/**
 * Intelligence Report Generator Component
 */
import { useState } from 'react';
import axios from 'axios';

interface IntelligenceReportGeneratorProps {
  onReportGenerated?: (report: any) => void;
}

const SERVICE_CATEGORIES = [
  { value: 'lawn_care', label: 'Lawn Care' },
  { value: 'security', label: 'Security' },
  { value: 'it_services', label: 'IT Services' },
  { value: 'fireworks', label: 'Fireworks' },
  { value: 'home_improvement', label: 'Home Improvement' },
  { value: 'general', label: 'General' },
];

export default function IntelligenceReportGenerator({
  onReportGenerated,
}: IntelligenceReportGeneratorProps) {
  const [geographyId, setGeographyId] = useState<string>('');
  const [zipCodes, setZipCodes] = useState<string>('');
  const [serviceCategory, setServiceCategory] = useState<string>('general');
  const [reportName, setReportName] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async () => {
    if (!geographyId || !zipCodes) {
      setError('Geography ID and ZIP codes are required');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/intelligence/reports`,
        {
          geography_id: parseInt(geographyId),
          zip_codes: zipCodes,
          service_category: serviceCategory,
          report_name: reportName || undefined,
        }
      );

      setReport(response.data);
      if (onReportGenerated) {
        onReportGenerated(response.data);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate report');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-4">
        Generate Intelligence Report
      </h2>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Geography ID
          </label>
          <input
            type="number"
            value={geographyId}
            onChange={(e) => setGeographyId(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            placeholder="Enter geography ID"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            ZIP Codes (comma-separated)
          </label>
          <input
            type="text"
            value={zipCodes}
            onChange={(e) => setZipCodes(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            placeholder="12345, 12346, 12347"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Service Category
          </label>
          <select
            value={serviceCategory}
            onChange={(e) => setServiceCategory(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
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
            value={reportName}
            onChange={(e) => setReportName(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            placeholder="My Custom Report"
          />
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        <button
          onClick={handleGenerate}
          disabled={loading}
          className="w-full bg-primary-600 text-white py-2 px-4 rounded-md hover:bg-primary-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          {loading ? 'Generating...' : 'Generate Report'}
        </button>
      </div>

      {report && (
        <div className="mt-6 p-4 bg-gray-50 rounded-lg">
          <h3 className="font-semibold text-lg mb-2">Report Summary</h3>
          <div className="space-y-2 text-sm">
            <p>
              <span className="font-medium">Total Households:</span>{' '}
              {report.total_households}
            </p>
            <p>
              <span className="font-medium">Target Households:</span>{' '}
              {report.target_households}
            </p>
            <p>
              <span className="font-medium">Average Demand Score:</span>{' '}
              {report.average_demand_score?.toFixed(2)}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

