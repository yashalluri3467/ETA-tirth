import React, { useState } from 'react';
import EtaForm from './components/EtaForm';
import EtaResult from './components/EtaResult';
import MapView from './components/MapView';
import EtaBreakdownCard from './components/EtaBreakdownCard';
import RouteSelector, { RouteOptionData } from './components/RouteSelector';
import ChatWidget from './components/ChatWidget';
import AdminDashboard from './components/AdminDashboard';
import { Compass, Bot, ShieldAlert, Sparkles } from 'lucide-react';
import './styles/theme.css';

function App() {
  const [activeTab, setActiveTab] = useState<'planner' | 'chat' | 'admin'>('planner');
  const [etaResult, setEtaResult] = useState<any>(null);
  const [routeOptions, setRouteOptions] = useState<RouteOptionData[]>([]);
  const [selectedRouteId, setSelectedRouteId] = useState<string>('route_fastest');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [currentCoords, setCurrentCoords] = useState({ lat: 19.9975, lng: 73.7898 });
  const [destCoords, setDestCoords] = useState({ lat: 19.9956, lng: 73.7810 });
  const [currentTravelMode, setCurrentTravelMode] = useState('driving');

  const apiBase = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  const handleEtaSubmit = async (data: {
    deviceId: string;
    currentLat: number;
    currentLng: number;
    destLat: number;
    destLng: number;
    crowdDensityIndex: number;
    isFestival: boolean;
    weatherSeverity: number;
    travelMode: string;
  }) => {
    setLoading(true);
    setError(null);
    setEtaResult(null);
    setCurrentCoords({ lat: data.currentLat, lng: data.currentLng });
    setDestCoords({ lat: data.destLat, lng: data.destLng });
    setCurrentTravelMode(data.travelMode);

    const isoTimestamp = new Date().toISOString().split('.')[0] + 'Z';

    const payload = {
      device_id: data.deviceId,
      timestamp: isoTimestamp,
      current_location: { lat: data.currentLat, lng: data.currentLng },
      destination: { lat: data.destLat, lng: data.destLng },
      crowd_density_index: data.crowdDensityIndex,
      is_festival: data.isFestival,
      weather_severity: data.weatherSeverity,
      travel_mode: data.travelMode,
    };

    try {
      // 1. Fetch Primary ETA
      const response = await fetch(`${apiBase}/api/v1/eta`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        let errMessage = `HTTP ${response.status}`;
        if (typeof errData.detail === 'string') {
          errMessage = errData.detail;
        } else if (Array.isArray(errData.detail)) {
          errMessage = errData.detail.map((e: any) => e.msg || JSON.stringify(e)).join(', ');
        }
        throw new Error(errMessage);
      }

      const result = await response.json();
      setEtaResult(result);

      // 2. Fetch Multi-Route Alternatives
      const routesRes = await fetch(`${apiBase}/api/v1/routes`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (routesRes.ok) {
        const routesData = await routesRes.json();
        setRouteOptions(routesData.routes || []);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to compute ETA');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      {/* Header Navigation */}
      <header className="app-header">
        <div className="header-brand">
          <div className="brand-icon">🕉️</div>
          <div className="brand-title">
            <h1>TirthTrack</h1>
            <p>Smart Pilgrimage Routing & Queue AI</p>
          </div>
        </div>

        <nav className="nav-tabs">
          <button
            className={`nav-btn ${activeTab === 'planner' ? 'active' : ''}`}
            onClick={() => setActiveTab('planner')}
          >
            <Compass size={18} /> ETA & Route Map
          </button>
          <button
            className={`nav-btn ${activeTab === 'chat' ? 'active' : ''}`}
            onClick={() => setActiveTab('chat')}
          >
            <Bot size={18} /> Pilgrim AI Assistant
          </button>
          <button
            className={`nav-btn ${activeTab === 'admin' ? 'active' : ''}`}
            onClick={() => setActiveTab('admin')}
          >
            <ShieldAlert size={18} /> Police Command Center
          </button>
        </nav>
      </header>

      {/* Main View Area */}
      <main className="app-main">
        {activeTab === 'planner' && (
          <div className="planner-grid">
            {/* Form Section */}
            <div>
              <EtaForm onSubmit={handleEtaSubmit} loading={loading} />
              {error && <div className="error-banner" style={{ marginTop: '1rem' }}>{error}</div>}
            </div>

            {/* Results & Live Map Section */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div className="glass-card" style={{ padding: '0.75rem' }}>
                <div style={{ fontWeight: 700, marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.95rem' }}>
                  <Sparkles size={16} color="var(--secondary)" /> Interactive Pilgrimage Map & Route Geometry
                </div>
                <MapView
                  currentLat={currentCoords.lat}
                  currentLng={currentCoords.lng}
                  destLat={destCoords.lat}
                  destLng={destCoords.lng}
                />
              </div>

              {etaResult && <EtaResult result={etaResult} />}

              {etaResult && <EtaBreakdownCard breakdown={etaResult.breakdown} travelMode={currentTravelMode} />}

              {routeOptions.length > 0 && (
                <RouteSelector
                  routes={routeOptions}
                  selectedRouteId={selectedRouteId}
                  onSelectRoute={(id) => setSelectedRouteId(id)}
                />
              )}
            </div>
          </div>
        )}

        {activeTab === 'chat' && (
          <ChatWidget
            apiBaseUrl={apiBase}
            currentLat={currentCoords.lat}
            currentLng={currentCoords.lng}
            destLat={destCoords.lat}
            destLng={destCoords.lng}
          />
        )}

        {activeTab === 'admin' && (
          <AdminDashboard apiBaseUrl={apiBase} />
        )}
      </main>
    </div>
  );
}

export default App;
