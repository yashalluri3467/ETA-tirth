import React from 'react';

interface BreakdownData {
  driving_time_seconds: number;
  parking_time_seconds: number;
  walking_time_seconds: number;
  queue_time_seconds: number;
  security_check_seconds: number;
  weather_delay_seconds: number;
  festival_delay_seconds: number;
  total_seconds: number;
}

interface EtaBreakdownCardProps {
  breakdown?: BreakdownData;
  travelMode?: string;
}

const formatMinutes = (seconds: number) => {
  const mins = Math.round(seconds / 60);
  if (mins < 60) return `${mins} min${mins !== 1 ? 's' : ''}`;
  const hrs = Math.floor(mins / 60);
  const remMins = mins % 60;
  return `${hrs} hr ${remMins} min`;
};

const EtaBreakdownCard: React.FC<EtaBreakdownCardProps> = ({ breakdown, travelMode = 'driving' }) => {
  if (!breakdown) return null;

  const total = breakdown.total_seconds || 1;

  const items = [
    {
      label: travelMode === 'walking' ? 'Walking Travel' : 'Road Driving',
      seconds: breakdown.driving_time_seconds,
      colorClass: 'fill-driving',
      icon: travelMode === 'walking' ? '🚶' : '🚗',
    },
    {
      label: 'Parking & Arrival',
      seconds: breakdown.parking_time_seconds,
      colorClass: 'fill-parking',
      icon: '🅿️',
    },
    {
      label: 'Walk to Entry Gate',
      seconds: breakdown.walking_time_seconds,
      colorClass: 'fill-walking',
      icon: '🚶‍♂️',
    },
    {
      label: 'Security Check & Screening',
      seconds: breakdown.security_check_seconds,
      colorClass: 'fill-security',
      icon: '🛡️',
    },
    {
      label: 'Temple Darshan Queue Wait',
      seconds: breakdown.queue_time_seconds,
      colorClass: 'fill-queue',
      icon: '🏛️',
    },
  ];

  return (
    <div className="glass-card" style={{ marginTop: '1rem' }}>
      <div className="card-header">
        <h3 className="card-title">
          <span>⏱️</span> Comprehensive ETA Breakdown
        </h3>
        <span style={{ fontSize: '0.9rem', color: 'var(--secondary)', fontWeight: 700 }}>
          Total: {formatMinutes(total)}
        </span>
      </div>

      <div className="breakdown-list">
        {items.map((item, idx) => {
          if (item.seconds <= 0) return null;
          const percent = Math.min(100, Math.round((item.seconds / total) * 100));

          return (
            <div key={idx} className="breakdown-item">
              <div className="breakdown-header">
                <span>
                  {item.icon} {item.label}
                </span>
                <span style={{ color: 'var(--text-muted)' }}>
                  {formatMinutes(item.seconds)} ({percent}%)
                </span>
              </div>
              <div className="breakdown-bar-bg">
                <div
                  className={`breakdown-bar-fill ${item.colorClass}`}
                  style={{ width: `${percent}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default EtaBreakdownCard;
