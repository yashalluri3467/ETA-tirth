import React from 'react';

export interface RouteOptionData {
  route_id: string;
  name: string;
  mode: string;
  distance_meters: number;
  duration_seconds: number;
  crowd_level: string;
  traffic_level: string;
  recommended: boolean;
}

interface RouteSelectorProps {
  routes: RouteOptionData[];
  selectedRouteId: string;
  onSelectRoute: (routeId: string) => void;
}

const RouteSelector: React.FC<RouteSelectorProps> = ({ routes, selectedRouteId, onSelectRoute }) => {
  if (!routes || routes.length === 0) return null;

  return (
    <div className="glass-card" style={{ marginTop: '1rem' }}>
      <h3 className="card-title">
        <span>🛤️</span> Recommended Route Options
      </h3>

      <div className="routes-grid">
        {routes.map((rt) => {
          const isSelected = rt.route_id === selectedRouteId;
          const durationMins = Math.round(rt.duration_seconds / 60);

          return (
            <div
              key={rt.route_id}
              className={`route-card ${isSelected ? 'selected' : ''}`}
              onClick={() => onSelectRoute(rt.route_id)}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span className={`badge ${rt.recommended ? 'badge-recommended' : 'badge-alternative'}`}>
                  {rt.mode}
                </span>
                {rt.recommended && <span style={{ fontSize: '0.75rem', color: '#34d399' }}>★ Best Choice</span>}
              </div>

              <div style={{ fontWeight: 700, fontSize: '0.95rem', marginTop: '0.25rem' }}>
                {rt.name}
              </div>

              <div style={{ fontSize: '1.2rem', fontWeight: 800, color: 'var(--secondary)' }}>
                {durationMins} mins
              </div>

              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                Distance: {(rt.distance_meters / 1000).toFixed(1)} km • Crowd: {rt.crowd_level}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default RouteSelector;
