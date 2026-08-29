import React, { useState } from 'react';
import { Send, Bot, User, Sparkles } from 'lucide-react';

interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  recommendations?: any;
}

interface ChatWidgetProps {
  apiBaseUrl: string;
  currentLat: number;
  currentLng: number;
  destLat: number;
  destLng: number;
}

const ChatWidget: React.FC<ChatWidgetProps> = ({ apiBaseUrl, currentLat, currentLng, destLat, destLng }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      sender: 'assistant',
      text: 'Hari Om! I am your TirthTrack AI Pilgrim Assistant. Ask me about ETAs, temple darshan queue wait times, or optimal departure hours!',
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const quickPrompts = [
    'What is the current darshan queue wait time?',
    'When is the best time to leave for the temple?',
    'Are there alternate gates with shorter lines?',
  ];

  const handleSend = async (textToSend?: string) => {
    const query = textToSend || input;
    if (!query.trim() || loading) return;

    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      sender: 'user',
      text: query,
    };

    setMessages((prev) => [...prev, userMsg]);
    if (!textToSend) setInput('');
    setLoading(true);

    try {
      const response = await fetch(`${apiBaseUrl}/api/v1/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          device_id: 'web_client_user',
          message: query,
          current_location: { lat: currentLat, lng: currentLng },
          destination: { lat: destLat, lng: destLng },
          crowd_density_index: 0.6,
          is_festival: false,
        }),
      });

      if (!response.ok) throw new Error('Assistant unavailable');
      const data = await response.json();

      const assistantMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        sender: 'assistant',
        text: data.reply,
        recommendations: data.recommendations,
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          sender: 'assistant',
          text: 'Apologies, I am having trouble fetching live queue data. Please try again shortly.',
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-card chat-container">
      <div className="card-header">
        <h3 className="card-title">
          <Bot size={22} color="var(--secondary)" /> AI Pilgrim Assistant
        </h3>
        <span style={{ fontSize: '0.75rem', color: '#34d399', fontWeight: 600 }}>● Online</span>
      </div>

      {/* Suggested Chips */}
      <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginBottom: '0.5rem' }}>
        {quickPrompts.map((prompt, idx) => (
          <button
            key={idx}
            className="badge badge-alternative"
            style={{ cursor: 'pointer', background: 'rgba(255,255,255,0.06)' }}
            onClick={() => handleSend(prompt)}
          >
            <Sparkles size={12} style={{ marginRight: 4 }} /> {prompt}
          </button>
        ))}
      </div>

      <div className="chat-messages">
        {messages.map((msg) => (
          <div key={msg.id} className={`msg-bubble ${msg.sender === 'user' ? 'msg-user' : 'msg-assistant'}`}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', marginBottom: '0.2rem', opacity: 0.85, fontSize: '0.75rem' }}>
              {msg.sender === 'user' ? <User size={14} /> : <Bot size={14} />}
              <span>{msg.sender === 'user' ? 'You' : 'Tirth AI'}</span>
            </div>
            <div>{msg.text}</div>
            {msg.recommendations && (
              <div style={{ marginTop: '0.5rem', padding: '0.4rem 0.6rem', background: 'rgba(0,0,0,0.2)', borderRadius: 6, fontSize: '0.8rem' }}>
                {msg.recommendations.suggested_gate && <div>📍 <strong>Suggested Entry:</strong> {msg.recommendations.suggested_gate}</div>}
                {msg.recommendations.best_departure_window && <div>⏱️ <strong>Best Departure Window:</strong> {msg.recommendations.best_departure_window}</div>}
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className="msg-bubble msg-assistant" style={{ fontStyle: 'italic', color: 'var(--text-muted)' }}>
            Tirth AI is calculating crowd models...
          </div>
        )}
      </div>

      <div className="chat-input-bar">
        <input
          type="text"
          className="input-field"
          placeholder="Ask a question about queue wait or ETAs..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
        />
        <button className="btn-primary" style={{ width: 'auto', padding: '0 1.25rem' }} onClick={() => handleSend()} disabled={loading}>
          <Send size={18} />
        </button>
      </div>
    </div>
  );
};

export default ChatWidget;
