import { useState } from 'react';

export default function Home() {
  const [title, setTitle] = useState('');
  const [buyPrice, setBuyPrice] = useState('');
  const [sellPrice, setSellPrice] = useState('');
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState('');

  const analyzeProduct = async () => {
    if (!title || !buyPrice || !sellPrice) {
      setError('Completa título, precio de compra y precio de venta');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title,
          buy_price: parseFloat(buyPrice),
          estimated_sell_price: parseFloat(sellPrice),
          url: url || '',
          image_url: '',
          location: ''
        })
      });

      const data = await response.json();
      
      if (data.success) {
        setResult(data.analysis);
      } else {
        setError(data.error || 'Error en el análisis');
      }
    } catch (e: any) {
      setError('Error conectando con el backend: ' + e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: 24, maxWidth: 1200, margin: '0 auto', fontFamily: 'system-ui, -apple-system, sans-serif' }}>
      <div style={{ marginBottom: 32 }}>
        <h1 style={{ margin: 0, fontSize: 36, fontWeight: 700 }}>🎯 Arbitraje Inteligente</h1>
        <p style={{ margin: '8px 0 0 0', fontSize: 16, color: '#666' }}>
          Analiza productos manualmente
        </p>
      </div>

      <div style={cardStyle}>
        <h2 style={{ marginTop: 0, fontSize: 20 }}>📊 Analizar Producto</h2>
        
        <div style={{ marginBottom: 16 }}>
          <label style={labelStyle}>Título del producto *</label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Ej: Game Boy Color Azul"
            style={inputStyle}
          />
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 16 }}>
          <div>
            <label style={labelStyle}>Precio de compra (€) *</label>
            <input
              type="number"
              value={buyPrice}
              onChange={(e) => setBuyPrice(e.target.value)}
              placeholder="30"
              style={inputStyle}
            />
          </div>
          <div>
            <label style={labelStyle}>Precio de venta estimado (€) *</label>
            <input
              type="number"
              value={sellPrice}
              onChange={(e) => setSellPrice(e.target.value)}
              placeholder="60"
              style={inputStyle}
            />
          </div>
        </div>

        <div style={{ marginBottom: 20 }}>
          <label style={labelStyle}>URL (opcional)</label>
          <input
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://es.wallapop.com/item/..."
            style={inputStyle}
          />
        </div>

        <button 
          onClick={analyzeProduct}
          disabled={loading}
          style={{
            ...buttonStyle,
            width: '100%',
            padding: 16,
            fontSize: 16,
            fontWeight: 700,
            backgroundColor: loading ? '#ccc' : '#0070f3'
          }}
        >
          {loading ? '⏳ Analizando...' : '🚀 Analizar Oportunidad'}
        </button>
      </div>

      {error && (
        <div style={{ background: '#fee', padding: 16, borderRadius: 8, marginTop: 16, color: '#c00', border: '1px solid #fcc' }}>
          ❌ {error}
        </div>
      )}

      {result && (
        <div style={{ ...cardStyle, marginTop: 24 }}>
          <h3 style={{ marginTop: 0 }}>📊 Resultado del Análisis</h3>
          
          <div style={{ display: 'flex', gap: 16, marginBottom: 20 }}>
            <div style={statStyle}>
              <div style={{ fontSize: 32, fontWeight: 700, color: result.net_profit > 0 ? '#0070f3' : '#c00' }}>
                {result.net_profit > 0 ? '+' : ''}{result.net_profit}€
              </div>
              <div style={{ fontSize: 14, color: '#666' }}>Beneficio Neto</div>
            </div>
            
            <div style={statStyle}>
              <div style={{ fontSize: 32, fontWeight: 700, color: '#fdcb6e' }}>
                {result.roi_percent}%
              </div>
              <div style={{ fontSize: 14, color: '#666' }}>ROI</div>
            </div>
            
            <div style={statStyle}>
              <div style={{ fontSize: 32, fontWeight: 700, color: '#00b894' }}>
                {result.score}
              </div>
              <div style={{ fontSize: 14, color: '#666' }}>Score</div>
            </div>
          </div>

          <div style={{
            padding: 16,
            borderRadius: 8,
            background: result.score >= 65 ? '#e8f5e9' : result.score >= 50 ? '#fff3e0' : '#ffebee',
            marginBottom: 20,
            fontSize: 16,
            fontWeight: 600
          }}>
            {result.recommendation}
          </div>

          <div style={{ marginBottom: 16 }}>
            <h4 style={{ margin: '0 0 12px 0' }}>💰 Desglose de Costes</h4>
            <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '8px 16px', fontSize: 14 }}>
              <div>Precio de compra:</div>
              <div style={{ textAlign: 'right', fontWeight: 600 }}>{result.costs_breakdown.buy_price}€</div>
              
              <div>Comisión compra:</div>
              <div style={{ textAlign: 'right' }}>{result.costs_breakdown.buy_commission}€</div>
              
              <div>Comisión venta:</div>
              <div style={{ textAlign: 'right' }}>{result.costs_breakdown.sell_commission}€</div>
              
              <div>Comisión pago:</div>
              <div style={{ textAlign: 'right' }}>{result.costs_breakdown.payment_fee}€</div>
              
              <div>Envío:</div>
              <div style={{ textAlign: 'right' }}>{result.costs_breakdown.sell_shipping}€</div>
              
              <div>Embalaje:</div>
              <div style={{ textAlign: 'right' }}>{result.costs_breakdown.packaging}€</div>
              
              <div>Impuestos (19%):</div>
              <div style={{ textAlign: 'right' }}>{result.costs_breakdown.taxes}€</div>
              
              <div>Coste de riesgo:</div>
              <div style={{ textAlign: 'right' }}>{result.costs_breakdown.risk_cost}€</div>
              
              <div style={{ borderTop: '2px solid #333', paddingTop: 8, fontWeight: 700 }}>INVERSIÓN TOTAL:</div>
              <div style={{ borderTop: '2px solid #333', paddingTop: 8, textAlign: 'right', fontWeight: 700 }}>
                {result.costs_breakdown.total_investment}€
              </div>
            </div>
          </div>

          <div style={{ marginBottom: 16 }}>
            <h4 style={{ margin: '0 0 8px 0' }}>⚠️ Análisis de Riesgo</h4>
            <div style={{ fontSize: 14 }}>
              <div>• Tiempo estimado de venta: <strong>{result.risk_adjusted.expected_days_to_sell} días</strong></div>
              <div>• Riesgo de no vender: <strong>{result.risk_adjusted.no_sale_risk}%</strong></div>
              <div>• Riesgo de devolución: <strong>{result.risk_adjusted.return_risk}%</strong></div>
              <div>• Precio breakeven: <strong>{result.breakeven_price}€</strong></div>
            </div>
          </div>

          {url && (
            <a 
              href={url}
              target="_blank"
              rel="noopener noreferrer"
              style={{
                ...buttonStyle,
                textDecoration: 'none',
                display: 'inline-block',
                backgroundColor: '#00b894'
              }}
            >
              Ver Producto en Wallapop →
            </a>
          )}
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
  padding: '10px 12px',
  border: '1px solid #ddd',
  borderRadius: 6,
  fontSize: 14,
  boxSizing: 'border-box'
};

const buttonStyle: React.CSSProperties = {
  padding: '10px 20px',
  border: 'none',
  borderRadius: 6,
  fontSize: 14,
  fontWeight: 500,
  cursor: 'pointer',
  backgroundColor: '#0070f3',
  color: 'white'
};

const labelStyle: React.CSSProperties = {
  display: 'block',
  marginBottom: 6,
  fontSize: 14,
  fontWeight: 600,
  color: '#333'
};

const statStyle: React.CSSProperties = {
  flex: 1,
  textAlign: 'center',
  padding: 16,
  background: '#f8f9fa',
  borderRadius: 8
};
