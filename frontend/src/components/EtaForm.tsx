import React, { useState } from 'react';
import { Navigation, Car, Footprints, CloudRain, Sparkles } from 'lucide-react';

interface EtaFormProps {
  onSubmit: (data: {
    deviceId: string;
    currentLat: number;
    currentLng: number;
    destLat: number;
    destLng: number;
    crowdDensityIndex: number;
    isFestival: boolean;
    weatherSeverity: number;
    travelMode: string;
  }) => void;
  loading: boolean;
}

const EtaForm: React.FC<EtaFormProps> = ({ onSubmit, loading }) => {
  const [deviceId, setDeviceId] = useState('pilgrim_001');
  const [currentLat, setCurrentLat] = useState('19.9975');
  const [currentLng, setCurrentLng] = useState('73.7898');
  const [destLat, setDestLat] = useState('19.9956');
  const [destLng, setDestLng] = useState('73.7810');
  const [crowdDensityIndex, setCrowdDensityIndex] = useState(0.6);
  const [isFestival, setIsFestival] = useState(false);
  const [weatherSeverity, setWeatherSeverity] = useState(0.1);
  const [travelMode, setTravelMode] = useState('driving');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      deviceId,
      currentLat: parseFloat(currentLat),
      currentLng: parseFloat(currentLng),
      destLat: parseFloat(destLat),
      destLng: parseFloat(destLng),
      crowdDensityIndex,
      isFestival,
      weatherSeverity,
      travelMode,
    });
  };

  return (
    <form className="glass-card form-section" onSubmit={handleSubmit}>
      <div className="card-header">
        <h3 className="card-title">
          <Navigation size={22} color="var(--primary)" /> Route & Crowd Parameters
        </h3>
      </div>

      <div>
        <label className="input-label">Device Identifier</label>
        <input
          type="text"
          className="input-field"
          value={deviceId}
          onChange={(e) => setDeviceId(e.target.value)}
          required
        />
      </div>

      <div>
        <label className="input-label">Current GPS Origin</label>
        <div className="coord-row">
          <input
            type="number"
            step="any"
            className="input-field"
            placeholder="Latitude"
            value={currentLat}
            onChange={(e) => setCurrentLat(e.target.value)}
            required
          />
          <input
            type="number"
            step="any"
            className="input-field"
            placeholder="Longitude"
            value={currentLng}
            onChange={(e) => setCurrentLng(e.target.value)}
            required
          />
        </div>
      </div>

      <div>
        <label className="input-label">Temple Destination GPS</label>
        <div className="coord-row">
          <input
            type="number"
            step="any"
            className="input-field"
            placeholder="Latitude"
            value={destLat}
            onChange={(e) => setDestLat(e.target.value)}
            required
          />
          <input
            type="number"
            step="any"
            className="input-field"
            placeholder="Longitude"
            value={destLng}
            onChange={(e) => setDestLng(e.target.value)}
            required
          />
        </div>
      </div>

      <div>
        <label className="input-label">Travel Mode</label>
        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <button
            type="button"
            className={`nav-btn ${travelMode === 'driving' ? 'active' : ''}`}
            style={{ flex: 1, justifyContent: 'center' }}
            onClick={() => setTravelMode('driving')}
          >
            <Car size={18} /> Driving
          </button>
          <button
            type="button"
            className={`nav-btn ${travelMode === 'walking' ? 'active' : ''}`}
            style={{ flex: 1, justifyContent: 'center' }}
            onClick={() => setTravelMode('walking')}
          >
            <Footprints size={18} /> Walking
          </button>
        </div>
      </div>

      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <label className="input-label">Crowd Density Index</label>
          <span style={{ fontSize: '0.85rem', color: 'var(--secondary)', fontWeight: 700 }}>
            {Math.round(crowdDensityIndex * 100)}%
          </span>
        </div>
        <input
          type="range"
          min="0"
          max="1"
          step="0.05"
          value={crowdDensityIndex}
          onChange={(e) => setCrowdDensityIndex(parseFloat(e.target.value))}
          style={{ width: '100%', accentColor: 'var(--primary)' }}
        />
      </div>

      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <label className="input-label" style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
            <CloudRain size={14} /> Weather Severity
          </label>
          <span style={{ fontSize: '0.85rem', color: 'var(--secondary)', fontWeight: 700 }}>
            {Math.round(weatherSeverity * 100)}%
          </span>
        </div>
        <input
          type="range"
          min="0"
          max="1"
          step="0.05"
          value={weatherSeverity}
          onChange={(e) => setWeatherSeverity(parseFloat(e.target.value))}
          style={{ width: '100%', accentColor: 'var(--secondary)' }}
        />
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginTop: '0.25rem' }}>
        <input
          type="checkbox"
          id="isFestival"
          checked={isFestival}
          onChange={(e) => setIsFestival(e.target.checked)}
          style={{ width: 18, height: 18, accentColor: 'var(--accent-gold)' }}
        />
        <label htmlFor="isFestival" style={{ cursor: 'pointer', fontSize: '0.9rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <Sparkles size={16} color="var(--accent-gold)" /> Mahashivratri / Special Festival Active
        </label>
      </div>

      <button type="submit" disabled={loading} className="btn-primary" style={{ marginTop: '0.75rem' }}>
        {loading ? 'Recalculating ETA...' : 'Compute Route & ETA'}
      </button>
    </form>
  );
};

export default EtaForm;
