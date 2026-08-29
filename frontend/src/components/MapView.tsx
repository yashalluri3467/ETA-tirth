import React from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix leaflet default icon missing issue
const originIcon = L.divIcon({
  className: 'custom-map-icon origin-icon',
  html: `<div style="background:#6366f1; width:24px; height:24px; border-radius:50%; border:3px solid #fff; box-shadow:0 0 10px #6366f1;"></div>`,
  iconSize: [24, 24],
  iconAnchor: [12, 12],
});

const destIcon = L.divIcon({
  className: 'custom-map-icon dest-icon',
  html: `<div style="background:#ef4444; width:28px; height:28px; border-radius:50%; border:3px solid #fff; box-shadow:0 0 12px #ef4444; display:flex; align-items:center; justify-content:center; color:white; font-size:12px; font-weight:bold;">🛕</div>`,
  iconSize: [28, 28],
  iconAnchor: [14, 14],
});

interface MapViewProps {
  currentLat: number;
  currentLng: number;
  destLat: number;
  destLng: number;
  destinationName?: string;
}

const MapView: React.FC<MapViewProps> = ({
  currentLat,
  currentLng,
  destLat,
  destLng,
  destinationName = 'Trimbakeshwar Shiva Temple',
}) => {
  const centerLat = (currentLat + destLat) / 2;
  const centerLng = (currentLng + destLng) / 2;

  // Simple interpolated route coordinates for visual representation
  const routePoints: [number, number][] = [
    [currentLat, currentLng],
    [currentLat + (destLat - currentLat) * 0.3, currentLng + (destLng - currentLng) * 0.25],
    [currentLat + (destLat - currentLat) * 0.7, currentLng + (destLng - currentLng) * 0.75],
    [destLat, destLng],
  ];

  return (
    <div className="map-container">
      <MapContainer
        center={[centerLat, centerLng]}
        zoom={13}
        scrollWheelZoom={true}
        style={{ height: '100%', width: '100%' }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        {/* Origin Marker */}
        <Marker position={[currentLat, currentLng]} icon={originIcon}>
          <Popup>
            <strong>Your Current Location</strong><br />
            GPS: {currentLat.toFixed(4)}, {currentLng.toFixed(4)}
          </Popup>
        </Marker>

        {/* Destination Marker */}
        <Marker position={[destLat, destLng]} icon={destIcon}>
          <Popup>
            <strong>{destinationName}</strong><br />
            Main Pilgrimage Entrance Gate 1
          </Popup>
        </Marker>

        {/* Polyline Route */}
        <Polyline
          positions={routePoints}
          color="#6366f1"
          weight={5}
          opacity={0.8}
          dashArray="8, 8"
        />
      </MapContainer>
    </div>
  );
};

export default MapView;
