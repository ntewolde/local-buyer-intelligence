/**
 * Demand Heatmap Component
 * Shows demand scores by ZIP code
 */
import { useEffect, useState } from 'react';
import api from '../services/api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface DemandHeatmapProps {
  geographyId: number;
  serviceCategory: string;
}

export default function DemandHeatmap({
  geographyId,
  serviceCategory,
}: DemandHeatmapProps) {
  const [zipScores, setZipScores] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch intelligence report with ZIP demand scores
        const response = await api.get('/api/v1/intelligence/reports', {
          params: {
            geography_id: geographyId,
            service_category: serviceCategory,
            limit: 1,
          },
        });

        if (response.data && response.data.length > 0) {
          const report = response.data[0];
          const scores = report.zip_demand_scores || {};
          const formattedData = Object.entries(scores).map(([zip, score]) => ({
            zip_code: zip,
            demand_score: score,
          }));

          setZipScores(formattedData.sort((a, b) => b.demand_score - a.demand_score));
        }
      } catch (error) {
        console.error('Failed to fetch demand scores:', error);
      } finally {
        setLoading(false);
      }
    };

    if (geographyId && serviceCategory) {
      fetchData();
    }
  }, [geographyId, serviceCategory]);

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <p className="text-gray-500">Loading demand scores...</p>
      </div>
    );
  }

  if (zipScores.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <p className="text-gray-500">No demand score data available</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-bold text-gray-900 mb-4">
        Demand Scores by ZIP Code
      </h2>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={zipScores.slice(0, 10)}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="zip_code" />
          <YAxis domain={[0, 100]} />
          <Tooltip />
          <Legend />
          <Bar dataKey="demand_score" fill="#0ea5e9" name="Demand Score" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

