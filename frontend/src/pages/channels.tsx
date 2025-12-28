/**
 * Channel Management Page
 */
import { useState, useEffect } from 'react';
import Head from 'next/head';
import AuthGuard from '../components/AuthGuard';
import Navigation from '../components/Navigation';
import api from '../services/api';

interface Channel {
  id: string;
  name: string;
  channel_type: string;
  city: string | null;
  state: string | null;
  zip_code: string | null;
  estimated_reach: number | null;
  website: string | null;
}

interface Geography {
  id: number;
  name: string;
  state_code: string;
}

export default function ChannelsPage() {
  const [channels, setChannels] = useState<Channel[]>([]);
  const [geographies, setGeographies] = useState<Geography[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [selectedGeography, setSelectedGeography] = useState<number | null>(null);
  const [formData, setFormData] = useState({
    geography_id: '',
    channel_type: 'HOA',
    name: '',
    city: '',
    state: '',
    zip_code: '',
    estimated_reach: '',
    website: '',
    notes: '',
  });

  useEffect(() => {
    fetchChannels();
    fetchGeographies();
  }, []);

  const fetchChannels = async () => {
    try {
      const params: any = {};
      if (selectedGeography) {
        params.geography_id = selectedGeography;
      }
      const response = await api.get('/api/v1/channels/', { params });
      setChannels(response.data);
    } catch (error) {
      console.error('Failed to fetch channels:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchGeographies = async () => {
    try {
      const response = await api.get('/api/v1/geography/');
      setGeographies(response.data);
    } catch (error) {
      console.error('Failed to fetch geographies:', error);
    }
  };

  useEffect(() => {
    if (selectedGeography !== null) {
      fetchChannels();
    }
  }, [selectedGeography]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/api/v1/channels/', {
        ...formData,
        geography_id: formData.geography_id ? parseInt(formData.geography_id) : null,
        estimated_reach: formData.estimated_reach ? parseInt(formData.estimated_reach) : null,
      });
      setShowCreateForm(false);
      setFormData({
        geography_id: '',
        channel_type: 'HOA',
        name: '',
        city: '',
        state: '',
        zip_code: '',
        estimated_reach: '',
        website: '',
        notes: '',
      });
      fetchChannels();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to create channel');
    }
  };

  const handleDelete = async (channelId: string) => {
    if (!confirm('Are you sure you want to delete this channel?')) return;

    try {
      await api.delete(`/api/v1/channels/${channelId}`);
      fetchChannels();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to delete channel');
    }
  };

  return (
    <AuthGuard>
      <div className="min-h-screen bg-gray-50">
        <Head>
          <title>Channels - Local Buyer Intelligence Platform</title>
        </Head>

        <Navigation />

        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="mb-6 flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Channels</h1>
              <p className="mt-1 text-sm text-gray-500">
                Manage institutional channels and gatekeepers
              </p>
            </div>
            <button
              onClick={() => setShowCreateForm(!showCreateForm)}
              className="bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700"
            >
              {showCreateForm ? 'Cancel' : 'Add Channel'}
            </button>
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Filter by Geography
            </label>
            <select
              value={selectedGeography || ''}
              onChange={(e) => setSelectedGeography(e.target.value ? parseInt(e.target.value) : null)}
              className="border border-gray-300 rounded-md px-3 py-2"
            >
              <option value="">All Geographies</option>
              {geographies.map((geo) => (
                <option key={geo.id} value={geo.id}>
                  {geo.name}, {geo.state_code}
                </option>
              ))}
            </select>
          </div>

          {showCreateForm && (
            <div className="bg-white rounded-lg shadow p-6 mb-6">
              <h2 className="text-xl font-bold mb-4">Create New Channel</h2>
              <form onSubmit={handleCreate} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Channel Type</label>
                    <select
                      required
                      value={formData.channel_type}
                      onChange={(e) => setFormData({ ...formData, channel_type: e.target.value })}
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                    >
                      <option value="HOA">HOA</option>
                      <option value="PROPERTY_MANAGER">Property Manager</option>
                      <option value="SCHOOL">School</option>
                      <option value="CHURCH">Church</option>
                      <option value="VENUE">Venue</option>
                      <option value="MEDIA">Media</option>
                      <option value="COMMUNITY_NEWSLETTER">Community Newsletter</option>
                      <option value="OTHER">Other</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Name *</label>
                    <input
                      type="text"
                      required
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Geography</label>
                    <select
                      value={formData.geography_id}
                      onChange={(e) => setFormData({ ...formData, geography_id: e.target.value })}
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
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
                    <label className="block text-sm font-medium text-gray-700">City</label>
                    <input
                      type="text"
                      value={formData.city}
                      onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">State</label>
                    <input
                      type="text"
                      maxLength={2}
                      value={formData.state}
                      onChange={(e) => setFormData({ ...formData, state: e.target.value.toUpperCase() })}
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">ZIP Code</label>
                    <input
                      type="text"
                      value={formData.zip_code}
                      onChange={(e) => setFormData({ ...formData, zip_code: e.target.value })}
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Estimated Reach</label>
                    <input
                      type="number"
                      value={formData.estimated_reach}
                      onChange={(e) => setFormData({ ...formData, estimated_reach: e.target.value })}
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Website</label>
                    <input
                      type="url"
                      value={formData.website}
                      onChange={(e) => setFormData({ ...formData, website: e.target.value })}
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
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Location</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Reach</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {channels.map((channel) => (
                    <tr key={channel.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {channel.name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {channel.channel_type}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {[channel.city, channel.state, channel.zip_code].filter(Boolean).join(', ') || '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {channel.estimated_reach?.toLocaleString() || '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        {channel.website && (
                          <a
                            href={channel.website}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-primary-600 hover:text-primary-900 mr-4"
                          >
                            Website
                          </a>
                        )}
                        <button
                          onClick={() => handleDelete(channel.id)}
                          className="text-red-600 hover:text-red-900"
                        >
                          Delete
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

