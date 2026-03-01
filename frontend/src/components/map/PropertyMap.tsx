import { useEffect, useRef, useState, useCallback } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import type { MapLayer } from '../../types';

// Token set via environment variable
mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_TOKEN || '';

interface PropertyMapProps {
  onMapClick?: (lng: number, lat: number) => void;
  selectedCoords?: [number, number] | null;
}

const OTTAWA_CENTER: [number, number] = [-75.6972, 45.4215];
const OTTAWA_ZOOM = 12;

const LAYER_CONFIGS: Record<MapLayer, { label: string; color: string }> = {
  zoning: { label: 'Zoning', color: '#3b82f6' },
  parcels: { label: 'Parcels', color: '#10b981' },
  floodplain: { label: 'Floodplain', color: '#ef4444' },
  heritage: { label: 'Heritage', color: '#f59e0b' },
};

export default function PropertyMap({ onMapClick, selectedCoords }: PropertyMapProps) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<mapboxgl.Map | null>(null);
  const marker = useRef<mapboxgl.Marker | null>(null);
  const [activeLayers, setActiveLayers] = useState<Set<MapLayer>>(new Set(['parcels']));

  const initMap = useCallback(() => {
    if (!mapContainer.current || map.current) return;

    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: 'mapbox://styles/mapbox/light-v11',
      center: OTTAWA_CENTER,
      zoom: OTTAWA_ZOOM,
    });

    map.current.addControl(new mapboxgl.NavigationControl(), 'top-right');
    map.current.addControl(
      new mapboxgl.GeolocateControl({ trackUserLocation: false }),
      'top-right',
    );

    map.current.on('load', () => {
      // Add Ottawa zoning WMS layer source (GeoOttawa)
      map.current!.addSource('ottawa-zoning', {
        type: 'raster',
        tiles: [
          'https://maps.ottawa.ca/arcgis/services/Zoning/MapServer/WMSServer?SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&LAYERS=0&STYLES=&CRS=EPSG:3857&BBOX={bbox-epsg-3857}&WIDTH=256&HEIGHT=256&FORMAT=image/png&TRANSPARENT=true',
        ],
        tileSize: 256,
      });

      map.current!.addLayer(
        {
          id: 'zoning-layer',
          type: 'raster',
          source: 'ottawa-zoning',
          paint: { 'raster-opacity': 0.5 },
          layout: { visibility: 'none' },
        },
      );
    });

    map.current.on('click', (e) => {
      onMapClick?.(e.lngLat.lng, e.lngLat.lat);
    });
  }, [onMapClick]);

  useEffect(() => {
    initMap();
    return () => {
      map.current?.remove();
      map.current = null;
    };
  }, [initMap]);

  // Update marker when selected coords change
  useEffect(() => {
    if (!map.current) return;

    if (marker.current) {
      marker.current.remove();
      marker.current = null;
    }

    if (selectedCoords) {
      marker.current = new mapboxgl.Marker({ color: '#2563eb' })
        .setLngLat(selectedCoords)
        .addTo(map.current);

      map.current.flyTo({ center: selectedCoords, zoom: 16 });
    }
  }, [selectedCoords]);

  const toggleLayer = (layer: MapLayer) => {
    setActiveLayers((prev) => {
      const next = new Set(prev);
      if (next.has(layer)) {
        next.delete(layer);
      } else {
        next.add(layer);
      }

      // Toggle zoning WMS layer visibility
      if (map.current && layer === 'zoning') {
        const visibility = next.has('zoning') ? 'visible' : 'none';
        if (map.current.getLayer('zoning-layer')) {
          map.current.setLayoutProperty('zoning-layer', 'visibility', visibility);
        }
      }

      return next;
    });
  };

  return (
    <div className="relative w-full h-full">
      <div ref={mapContainer} className="w-full h-full" />

      {/* Layer toggles */}
      <div className="absolute bottom-4 left-4 bg-white rounded-lg shadow-lg p-3 space-y-2">
        <div className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">
          Map Layers
        </div>
        {(Object.entries(LAYER_CONFIGS) as [MapLayer, { label: string; color: string }][]).map(
          ([key, config]) => (
            <label key={key} className="flex items-center gap-2 cursor-pointer text-sm">
              <input
                type="checkbox"
                checked={activeLayers.has(key)}
                onChange={() => toggleLayer(key)}
                className="rounded border-gray-300"
              />
              <span
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: config.color }}
              />
              <span>{config.label}</span>
            </label>
          ),
        )}
      </div>

      {/* Coordinates display */}
      {selectedCoords && (
        <div className="absolute top-4 left-4 bg-white rounded-lg shadow px-3 py-1 text-xs text-gray-600">
          {selectedCoords[1].toFixed(4)}, {selectedCoords[0].toFixed(4)}
        </div>
      )}
    </div>
  );
}
