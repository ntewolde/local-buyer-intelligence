/**
 * Map Visualization Component using Mapbox
 */
import { useState, useMemo } from 'react';
import Map, { Marker, Popup } from 'react-map-gl';
import 'mapbox-gl/dist/mapbox-gl.css';

interface MapVisualizationProps {
  geographyId: number;
  serviceCategory: string;
}

export default function MapVisualization({
  geographyId,
  serviceCategory,
}: MapVisualizationProps) {
  const [popupInfo, setPopupInfo] = useState<any>(null);
  const mapboxToken = process.env.NEXT_PUBLIC_MAPBOX_TOKEN || '';

  // Default viewport (would be loaded from geography data)
  const [viewState, setViewState] = useState({
    longitude: -74.006,
    latitude: 40.7128,
    zoom: 10,
  });

  // TODO: Load actual geography data and ZIP code boundaries
  // This is a placeholder component structure

  if (!mapboxToken) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <p className="text-gray-500">
          Mapbox token not configured. Please set NEXT_PUBLIC_MAPBOX_TOKEN in your environment.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      <div className="p-4 border-b">
        <h2 className="text-xl font-bold text-gray-900">Demand Heatmap</h2>
        <p className="text-sm text-gray-500">
          Service Category: {serviceCategory}
        </p>
      </div>
      <div className="h-96">
        <Map
          {...viewState}
          onMove={(evt) => setViewState(evt.viewState)}
          mapboxAccessToken={mapboxToken}
          style={{ width: '100%', height: '100%' }}
          mapStyle="mapbox://styles/mapbox/light-v11"
        >
          {/* TODO: Add markers for demand signals and ZIP code boundaries */}
          {popupInfo && (
            <Popup
              longitude={popupInfo.longitude}
              latitude={popupInfo.latitude}
              anchor="bottom"
              onClose={() => setPopupInfo(null)}
            >
              <div className="p-2">
                <p className="font-semibold">{popupInfo.title}</p>
                <p className="text-sm text-gray-600">
                  Demand Score: {popupInfo.demandScore}
                </p>
              </div>
            </Popup>
          )}
        </Map>
      </div>
    </div>
  );
}






