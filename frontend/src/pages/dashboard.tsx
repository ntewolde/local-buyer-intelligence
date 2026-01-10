/**
 * Local Buyer Intelligence Platform - Main Dashboard
 */
import { useState } from 'react';
import Head from 'next/head';
import AuthGuard from '../components/AuthGuard';
import Navigation from '../components/Navigation';
import IntelligenceReportGenerator from '../components/IntelligenceReportGenerator';
import MapVisualization from '../components/MapVisualization';
import DemandHeatmap from '../components/DemandHeatmap';

export default function Dashboard() {
  const [selectedGeography, setSelectedGeography] = useState<number | null>(null);
  const [selectedServiceCategory, setSelectedServiceCategory] = useState<string>('general');

  return (
    <AuthGuard>
      <div className="min-h-screen bg-gray-50">
        <Head>
          <title>Dashboard - LocalBI</title>
          <meta name="description" content="Data-driven local demand intelligence without PII scraping" />
          <link rel="icon" href="/favicon.ico" />
        </Head>

        <Navigation />

        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="mb-6">
            <h1 className="text-3xl font-bold text-gray-900">
              Dashboard
            </h1>
            <p className="mt-1 text-sm text-gray-500">
              Generate intelligence reports and analyze buyer demand
            </p>
          </div>

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
    </AuthGuard>
  );
}
