import { useState } from 'react';

export default function Home() {
  const [keywords, setKeywords] = useState('');
  const [loading, setLoading] = useState(false);
  const [opportunities, setOpportunities] = useState<any[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [error, setError] = useState('');

  const searchArbitrage = async () => {
    if (!keywords.trim()) {
      setError('Introduce palabras clave para buscar');
      return;
    }

    setLoading(true);
    setError('');
    setOpportunities([]);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const keywordList = keywords.split(' ').filter(k => k.trim());
      
      const response = await fetch(`${apiUrl}/api/search-arbitrage`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          keywords: keywordList,
          max_results: 20
        })
      });

      const data = await response.json();
      
      if (data.success) {
        setOpportunities(data.opportunities || []);
        setStats(data.platforms_searched);
      } else {
        setError('Error en la búsqueda');
      }
    } catch (e: any) {
      setError('Error conectando con el backend: ' + e.message);
    } finally {
      setLoading(false);
    }
  };

  const getPlatformEmoji = (platform: string) => {
    const emojis: any = {
      'wallapop': '🛍️',
      'ebay': '🌐',
      'vinted': '👕',
      'catawiki': '🎨'
    };
    return emojis[platform] || '📦';
  };

  const getPlatformColor = (platform: string) => {
    const colors: any = {
      'wallapop': '#13c1ac',
      'ebay': '#e53238',
      'vinted': '#09b1ba',
      'catawiki': '#ff6f00'
    };
    return colors[platform] || '#666';
  };

  return (
    <div style={{ padding: 24, maxWidth: 1400, margin: '0 auto', fontFamily: 'system-ui, -apple-system, sans-serif' }}>
      <div style={{ marginBottom: 32 }}>
        <h1 style={{ margin: 0, fontSize: 36, fontWeight: 700 }}>🎯 Arbitraje Inteligente Multi-Plataforma</h1>
        <p style={{ margin: '8px 0 0 0', fontSize: 16, color: '#666' }}>
          Busca en Wallapop, eBay, Vinted y Catawiki simultáneamente
        </p>
      </div>

      <div style={cardStyle}>
        <h2 style={{ marginTop: 0, fontSize: 20 }}>🔍 Buscar Oportunidades de Arbitraje</h2>
        
        <div style={{ marginBottom: 20 }}>
          <label style={labelStyle}>Palabras clave (ej: game boy, pokemon, rolex)</label>
          <input
            type="text"
            value={keywords}
            onChange={(e) => setKeywords(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && searchArbitrage()}
            placeholder="game boy color"
            style={inputStyle}
          />
        </div>

        <button 
          onClick={searchArbitrage}
          disabled={loading}
          style={{
            ...buttonStyle,
            width: '100%',
            padding: 16,
            fontSize: 16,
            fontWeight: 700,
            backgroundColor: loading ? '#ccc' : '#0070f3',
            cursor: loading ? 'wait' : 'pointer'
          }}
        >
          {loading ? '⏳ Buscando en todas las plataformas...' : '🚀 Buscar Oportunidades'}
        </button>

        {loading && (
          <div style={{ marginTop: 16, padding: 12, background: '#e3f2fd', borderRadius: 6, fontSize: 14 }}>
            ⚡ Scraping Wallapop, eBay, Vinted y Catawiki en paralelo...
          </div>
        )}
      </div>

      {error && (
        <div style={{ background: '#fee', padding: 16, borderRadius: 8, marginTop: 16, color: '#c00', border: '1px solid #fcc' }}>
          ❌ {error}
        </div>
      )}

      {stats && (
        <div style={{ ...cardStyle, marginTop: 24, background: '#f8f9fa' }}>
          <h3 style={{ marginTop: 0, marginBottom: 16 }}>📊 Productos Encontrados</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16 }}>
            <div style={statBoxStyle}>
              <div style={{ fontSize: 24, fontWeight: 700, color: '#13c1ac' }}>🛍️ {stats.wallapop}</div>
              <div style={{ fontSize: 12, color: '#666' }}>Wallapop</div>
            </div>
            <div style={statBoxStyle}>
              <div style={{ fontSize: 24, fontWeight: 700, color: '#e53238' }}>🌐 {stats.ebay}</div>
              <div style={{ fontSize: 12, color: '#666' }}>eBay</div>
            </div>
            <div style={statBoxStyle}>
              <div style={{ fontSize: 24, fontWeight: 700, color: '#09b1ba' }}>👕 {stats.vinted}</div>
              <div style={{ fontSize: 12, color: '#666' }}>Vinted</div>
            </div>
            <div style={statBoxStyle}>
              <div style={{ fontSize: 24, fontWeight: 700, color: '#ff6f00' }}>🎨 {stats.catawiki}</div>
              <div style={{ fontSize: 12, color: '#666' }}>Catawiki</div>
            </div>
          </div>
        </div>
      )}

      {opportunities.length > 0 && (
        <div style={{ marginTop: 24 }}>
          <h2 style={{ marginBottom: 16 }}>💰 Mejores Oportunidades ({opportunities.length})</h2>
          
          {opportunities.map((opp, idx) => (
            <div key={idx} style={{ ...cardStyle, marginBottom: 16, background: opp.roi_percent >= 50 ? '#e8f5e9' : 'white' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 16 }}>
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
                    <span style={{ fontSize: 24, fontWeight: 700, color: opp.roi_percent >= 50 ? '#2e7d32' : '#ff6f00' }}>
                      #{idx + 1}
                    </span>
                    <span style={{ fontSize: 20, fontWeight: 700, color: opp.net_profit >= 0 ? '#2e7d32' : '#c62828' }}>
                      {opp.net_profit >= 0 ? '+' : ''}{opp.net_profit}€
                    </span>
                    <span style={{ fontSize: 16, color: '#666' }}>
                      ({opp.roi_percent}% ROI)
                    </span>
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: '1fr auto 1fr', gap: 16, alignItems: 'center' }}>
                    {/* COMPRAR */}
                    <div style={{ padding: 12, background: '#f8f9fa', borderRadius: 8 }}>
                      <div style={{ fontSize: 12, fontWeight: 600, color: '#666', marginBottom: 4 }}>
                        {getPlatformEmoji(opp.buy_platform)} COMPRAR EN
                      </div>
                      <div style={{ fontSize: 14, fontWeight: 700, color: getPlatformColor(opp.buy_platform), textTransform: 'uppercase', marginBottom: 8 }}>
                        {opp.buy_platform}
                      </div>
                      <div style={{ fontSize: 13, marginBottom: 8, height: 40, overflow: 'hidden' }}>
                        {opp.buy_title.substring(0, 60)}...
                      </div>
                      <div style={{ fontSize: 20, fontWeight: 700, marginBottom: 8 }}>
                        {opp.buy_price}€
                      </div>
                      {opp.buy_url && (
                        <a href={opp.buy_url} target="_blank" rel="noopener noreferrer" style={{ fontSize: 12, color: '#0070f3', textDecoration: 'none' }}>
                          Ver producto →
                        </a>
                      )}
                    </div>

                    {/* FLECHA */}
                    <div style={{ fontSize: 32, color: '#0070f3' }}>
                      →
                    </div>

                    {/* VENDER */}
                    <div style={{ padding: 12, background: '#f8f9fa', borderRadius: 8 }}>
                      <div style={{ fontSize: 12, fontWeight: 600, color: '#666', marginBottom: 4 }}>
                        {getPlatformEmoji(opp.sell_platform)} VENDER EN
                      </div>
                      <div style={{ fontSize: 14, fontWeight: 700, color: getPlatformColor(opp.sell_platform), textTransform: 'uppercase', marginBottom: 8 }}>
                        {opp.sell_platform}
                      </div>
                      <div style={{ fontSize: 13, marginBottom: 8, height: 40, overflow: 'hidden' }}>
                        {opp.sell_title.substring(0, 60)}...
                      </div>
                      <div style={{ fontSize: 20, fontWeight: 700, marginBottom: 8 }}>
                        {opp.sell_price}€
                      </div>
                      {opp.sell_url && (
                        <a href={opp.sell_url} target="_blank" rel="noopener noreferrer" style={{ fontSize: 12, color: '#0070f3', textDecoration: 'none' }}>
                          Ver producto →
                        </a>
                      )}
                    </div>
                  </div>

                  {/* COSTES */}
                  <details style={{ marginTop: 12 }}>
                    <summary style={{ cursor: 'pointer', fontSize: 13, color: '#666' }}>Ver desglose de costes</summary>
                    <div style={{ marginTop: 8, fontSize: 12, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 4 }}>
                      <div>Precio compra: {opp.costs_breakdown.buy_price}€</div>
                      <div>Comisión compra: {opp.costs_breakdown.buy_commission}€</div>
                      <div>Envío compra: {opp.costs_breakdown.buy_shipping}€</div>
                      <div>Comisión venta: {opp.costs_breakdown.sell_commission}€</div>
                      <div>Envío venta: {opp.costs_breakdown.sell_shipping}€</div>
                      <div>Comisión pago: {opp.costs_breakdown.payment_fee}€</div>
                      <div>Embalaje: {opp.costs_breakdown.packaging}€</div>
                      <div>Impuestos: {opp.costs_breakdown.taxes}€</div>
                      <div style={{ fontWeight: 700, borderTop: '1px solid #ddd', paddingTop: 4, marginTop: 4 }}>
                        Inversión total: {opp.total_investment}€
                      </div>
                    </div>
                  </details>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {!loading && opportunities.length === 0 && stats && (
        <div style={{ ...cardStyle, marginTop: 24, textAlign: 'center', padding: 40 }}>
          <div style={{ fontSize: 48, marginBottom: 16 }}>🔍</div>
          <div style={{ fontSize: 18, color: '#666' }}>
            No se encontraron oportunidades rentables con estos términos de búsqueda.
          </div>
          <div style={{ fontSize: 14, color: '#999', marginTop: 8 }}>
            Intenta con otras palabras clave o productos diferentes.
          </div>
        </div>
      )}
    </div>
  );
}

const cardStyle: React.CSSProperties = {
  background: 'white',
  border: '1px solid #e0e0e0',
  borderRadius: 12,
  padding: 24,
  boxShadow: '0 2px 8px rgba(0,0,0,0.08)'
};

const inputStyle: React.CSSProperties = {
  width: '100%',
  padding: '12px 16px',
  border: '2px solid #ddd',
  borderRadius: 8,
  fontSize: 16,
  boxSizing: 'border-box',
  transition: 'border-color 0.2s'
};

const buttonStyle: React.CSSProperties = {
  padding: '12px 24px',
  border: 'none',
  borderRadius: 8,
  fontSize: 16,
  fontWeight: 600,
  cursor: 'pointer',
  backgroundColor: '#0070f3',
  color: 'white',
  transition: 'all 0.2s'
};

const labelStyle: React.CSSProperties = {
  display: 'block',
  marginBottom: 8,
  fontSize: 14,
  fontWeight: 600,
  color: '#333'
};

const statBoxStyle: React.CSSProperties = {
  textAlign: 'center',
  padding: 16,
  background: 'white',
  borderRadius: 8,
  border: '1px solid #e0e0e0'
};