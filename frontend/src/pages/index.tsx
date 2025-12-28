/**
 * Local Buyer Intelligence Platform - Main Dashboard
 */
import { useState } from 'react';
import Head from 'next/head';
import IntelligenceReportGenerator from '../components/IntelligenceReportGenerator';
import MapVisualization from '../components/MapVisualization';
import DemandHeatmap from '../components/DemandHeatmap';

export default function Home() {
  const [selectedGeography, setSelectedGeography] = useState<number | null>(null);
  const [selectedServiceCategory, setSelectedServiceCategory] = useState<string>('general');

  return (
    <div className="min-h-screen bg-gray-50">
      <Head>
        <title>Local Buyer Intelligence Platform</title>
        <meta name="description" content="Data-driven local demand intelligence without PII scraping" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <h1 className="text-3xl font-bold text-gray-900">
            Local Buyer Intelligence Platform
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            Identify potential buyers in specific geographic areas across multiple service verticals
          </p>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Column - Report Generator */}
          <div className="space-y-6">
            <IntelligenceReportGenerator
              onReportGenerated={(report) => {
                setSelectedGeography(report.geography_id);
                setSelectedServiceCategory(report.service_category);
              }}
            />
          </div>

          {/* Right Column - Map and Visualizations */}
          <div className="space-y-6">
            {selectedGeography && (
              <>
                <MapVisualization
                  geographyId={selectedGeography}
                  serviceCategory={selectedServiceCategory}
                />
                <DemandHeatmap
                  geographyId={selectedGeography}
                  serviceCategory={selectedServiceCategory}
                />
              </>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

