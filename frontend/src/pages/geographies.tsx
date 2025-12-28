/**
 * Geography Management Page
 */
import { useState, useEffect } from 'react';
import Head from 'next/head';
import AuthGuard from '../components/AuthGuard';
import Navigation from '../components/Navigation';
import api from '../services/api';

interface Geography {
  id: number;
  name: string;
  type: string;
  state_code: string;
  census_last_refreshed_at: string | null;
  property_last_refreshed_at: string | null;
  events_last_refreshed_at: string | null;
  channels_last_refreshed_at: string | null;
}

export default function GeographiesPage() {
  const [geographies, setGeographies] = useState<Geography[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    type: 'city',
    state_code: '',
    county_name: '',
    latitude: '',
    longitude: '',
  });

  useEffect(() => {
    fetchGeographies();
  }, []);

  const fetchGeographies = async () => {
    try {
      const response = await api.get('/api/v1/geography/');
      setGeographies(response.data);
    } catch (error) {
      console.error('Failed to fetch geographies:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/api/v1/geography/', {
        ...formData,
        latitude: formData.latitude ? parseFloat(formData.latitude) : null,
        longitude: formData.longitude ? parseFloat(formData.longitude) : null,
      });
      setShowCreateForm(false);
      setFormData({
        name: '',
        type: 'city',
        state_code: '',
        county_name: '',
        latitude: '',
        longitude: '',
      });
      fetchGeographies();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to create geography');
    }
  };

  const handleRefreshCensus = async (geographyId: number) => {
    try {
      await api.post(`/api/v1/ingestion-runs/census/refresh?geography_id=${geographyId}`);
      alert('Census refresh started');
      fetchGeographies();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to start census refresh');
    }
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'Never';
    return new Date(dateString).toLocaleString();
  };

  return (
    <AuthGuard>
      <div className="min-h-screen bg-gray-50">
        <Head>
          <title>Geographies - Local Buyer Intelligence Platform</title>
        </Head>

        <Navigation />

        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="mb-6 flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Geographies</h1>
              <p className="mt-1 text-sm text-gray-500">
                Manage geographic areas and view data freshness
              </p>
            </div>
            <button
              onClick={() => setShowCreateForm(!showCreateForm)}
              className="bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700"
            >
              {showCreateForm ? 'Cancel' : 'Add Geography'}
            </button>
          </div>

          {showCreateForm && (
            <div className="bg-white rounded-lg shadow p-6 mb-6">
              <h2 className="text-xl font-bold mb-4">Create New Geography</h2>
              <form onSubmit={handleCreate} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Name</label>
                    <input
                      type="text"
                      required
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Type</label>
                    <select
                      value={formData.type}
                      onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                    >
                      <option value="city">City</option>
                      <option value="county">County</option>
                      <option value="state">State</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">State Code</label>
                    <input
                      type="text"
                      required
                      maxLength={2}
                      value={formData.state_code}
                      onChange={(e) => setFormData({ ...formData, state_code: e.target.value.toUpperCase() })}
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">County Name (optional)</label>
                    <input
                      type="text"
                      value={formData.county_name}
                      onChange={(e) => setFormData({ ...formData, county_name: e.target.value })}
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                    />
                  </div>
                </div>
                <div className="flex justify-end">
                  <button
                    type="submit"
                    className="bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700"
                  >
                    Create
                  </button>
                </div>
              </form>
            </div>
          )}

          {loading ? (
            <div className="text-center py-12">Loading...</div>
          ) : (
            <div className="bg-white shadow rounded-lg overflow-hidden">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Name
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      State
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Census
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Property
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {geographies.map((geo) => (
                    <tr key={geo.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {geo.name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {geo.type}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {geo.state_code}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <div className="flex items-center">
                          <span>{formatDate(geo.census_last_refreshed_at)}</span>
                          {(!geo.census_last_refreshed_at || new Date(geo.census_last_refreshed_at) < new Date(Date.now() - 30 * 24 * 60 * 60 * 1000)) && (
                            <span className="ml-2 text-yellow-600 text-xs">(Stale)</span>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatDate(geo.property_last_refreshed_at)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <button
                          onClick={() => handleRefreshCensus(geo.id)}
                          className="text-primary-600 hover:text-primary-900"
                        >
                          Refresh Census
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </main>
      </div>
    </AuthGuard>
  );
}






