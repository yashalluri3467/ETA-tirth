import React from 'react';
import { Clock, MapPin, Cpu, ShieldCheck } from 'lucide-react';

interface EtaResultProps {
  result: {
    status: string;
    device_id: string;
    route_distance_meters: number;
    travel_time_seconds: number;
    base_travel_time_seconds?: number;
    predicted_travel_time_seconds?: number;
    predicted_queue_time_seconds?: number;
    traffic_delay_factor?: number;
    remaining_distance_meters: number;
    eta: string;
    route_updated: boolean;
    ml_model_used?: boolean;
  };
}

const formatIsoTime = (isoStr: string) => {
  try {
    const d = new Date(isoStr);
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  } catch {
    return isoStr;
  }
};

const EtaResult: React.FC<EtaResultProps> = ({ result }) => {
  const travelMins = Math.round(result.travel_time_seconds / 60);
  const roadTravelMins = Math.round((result.predicted_travel_time_seconds || result.travel_time_seconds) / 60);
  const queueMins = Math.round((result.predicted_queue_time_seconds || 0) / 60);
  const distanceKm = (result.route_distance_meters / 1000).toFixed(1);

  return (
    <div className="glass-card" style={{ marginTop: '1rem' }}>
      <div className="card-header">
        <h3 className="card-title">
          <Clock size={22} color="var(--secondary)" /> Calculated Pilgrimage Arrival
        </h3>
        <span className={`badge ${result.ml_model_used ? 'badge-recommended' : 'badge-alternative'}`}>
          {result.ml_model_used ? <Cpu size={12} style={{ marginRight: 4 }} /> : null}
          {result.ml_model_used ? 'XGBoost ML Trained' : 'Heuristic Engine'}
        </span>
      </div>

      <div style={{ textAlign: 'center', margin: '1rem 0' }}>
        <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          Estimated Arrival Time
        </div>
        <div style={{ fontSize: '2.5rem', fontWeight: 800, background: 'linear-gradient(90deg, #6366f1, #06b6d4)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
          {formatIsoTime(result.eta)}
        </div>
        <div style={{ fontSize: '0.9rem', color: 'var(--text-main)', marginTop: '0.2rem' }}>
          Total Duration: <strong>{travelMins} mins</strong> ({distanceKm} km)
        </div>
      </div>

      <div className="stats-row" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))' }}>
        <div className="stat-box">
          <span className="stat-label">Road Travel</span>
          <div className="stat-num" style={{ fontSize: '1.25rem' }}>{roadTravelMins} min</div>
        </div>

        <div className="stat-box">
          <span className="stat-label">Darshan Queue</span>
          <div className="stat-num" style={{ fontSize: '1.25rem', color: 'var(--accent-red)' }}>{queueMins} min</div>
        </div>

        <div className="stat-box">
          <span className="stat-label">Traffic Factor</span>
          <div className="stat-num" style={{ fontSize: '1.25rem', color: 'var(--accent-gold)' }}>
            {result.traffic_delay_factor ? `${result.traffic_delay_factor}x` : '1.0x'}
          </div>
        </div>

        <div className="stat-box">
          <span className="stat-label">Route Status</span>
          <div className="stat-num" style={{ fontSize: '1.1rem', color: 'var(--accent-green)' }}>
            {result.route_updated ? 'Updated' : 'Cached'}
          </div>
        </div>
      </div>
    </div>
  );
};

export default EtaResult;
