import { useState } from 'react';

type PriceTarget = 'open' | 'low' | 'high' | 'close';

export function KronosForecastChart({
  symbol,
}: {
  symbol: string;
}) {
  const [forecastDate, setForecastDate] = useState('');
  const [target, setTarget] = useState<PriceTarget>('low');
  const [horizon, setHorizon] = useState('48');
  const [message, setMessage] = useState('');

  async function handlePreview() {
  if (!forecastDate) {
    setMessage('Please select a forecast date.');
    return;
  }

  const candles = Number(horizon);

  if (candles < 1 || candles > 48) {
    setMessage('Prediction candles must be between 1 and 48.');
    return;
  }

  setMessage('Generating forecast...');

  try {
    const response = await fetch('http://127.0.0.1:8000/api/forecasts/predict', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        symbol: symbol,
        forecast_date: forecastDate,
        target: target,
        horizon: candles,
      }),
    });

    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.detail || 'Forecast request failed.');
    }

    console.log('Kronos forecast:', result);
    setMessage('Forecast received successfully.');
  } catch (error) {
    setMessage(
      error instanceof Error ? error.message : 'Something went wrong.'
    );
  }
}
  return (
    <section
      className="section"
      style={{ marginTop: 'var(--space-5)' }}
    >
      <div className="page-header">
        <div className="page-title">
          {symbol} — Kronos Forecast
        </div>
        <div className="page-subtitle">
          Select a date and configure your prediction.
        </div>
      </div>

      {/* Forecast controls */}
      <div
        className="card"
        style={{ marginBottom: 'var(--space-4)' }}
      >
        <div
          style={{
            display: 'flex',
            flexWrap: 'wrap',
            gap: 'var(--space-4)',
            alignItems: 'flex-end',
          }}
        >
          <div>
            <label
              htmlFor="forecast-date"
              style={{
                display: 'block',
                fontSize: 12,
                color: 'var(--text-muted)',
                marginBottom: 6,
              }}
            >
              Forecast date
            </label>

            <input
              id="forecast-date"
              type="date"
              className="table-search"
              value={forecastDate}
              onChange={(e) => setForecastDate(e.target.value)}
              style={{ minWidth: 165 }}
            />
          </div>

          <div>
            <label
              htmlFor="forecast-target"
              style={{
                display: 'block',
                fontSize: 12,
                color: 'var(--text-muted)',
                marginBottom: 6,
              }}
            >
              Price to predict
            </label>

            <select
              id="forecast-target"
              className="table-search"
              value={target}
              onChange={(e) =>
                setTarget(e.target.value as PriceTarget)
              }
              style={{ minWidth: 130 }}
            >
              <option value="open">Open</option>
              <option value="low">Low</option>
              <option value="high">High</option>
              <option value="close">Close</option>
            </select>
          </div>

          <div>
            <label
              htmlFor="forecast-horizon"
              style={{
                display: 'block',
                fontSize: 12,
                color: 'var(--text-muted)',
                marginBottom: 6,
              }}
            >
              Prediction candles (maximum 48)
            </label>

            <select
              id="forecast-horizon"
              className="table-search"
              value={horizon}
              onChange={(e) => setHorizon(e.target.value)}
              style={{ minWidth: 130 }}
            >
              <option value="12">12 candles</option>
              <option value="24">24 candles</option>
              <option value="36">36 candles</option>
              <option value="48">48 candles</option>
            </select>
          </div>

          <button
            type="button"
            className="pagination-btn"
            style={{ padding: '9px 18px' }}
            onClick={handlePreview}
          >
            Prepare Forecast
          </button>
        </div>

        {message && (
          <div
            role="status"
            style={{
              marginTop: 'var(--space-3)',
              fontSize: 13,
              color: 'var(--text-secondary)',
            }}
          >
            {message}
          </div>
        )}
      </div>

      {/* Chart preview */}
      <div className="chart-wrapper">
        <div className="chart-title">
          Actual vs Predicted {target.toUpperCase()} — {symbol}
        </div>

        <div style={{ width: '100%', padding: '12px 0' }}>
          <svg
            viewBox="0 0 700 270"
            role="img"
            aria-label="Forecast chart preview; actual predictions are not connected yet"
            style={{ width: '100%', display: 'block' }}
          >
            {[40, 85, 130, 175, 220].map((y) => (
              <line
                key={y}
                x1="65"
                y1={y}
                x2="675"
                y2={y}
                stroke="var(--border)"
                strokeDasharray="4 4"
              />
            ))}

            <line
              x1="65"
              y1="25"
              x2="65"
              y2="220"
              stroke="var(--text-muted)"
            />

            <line
              x1="65"
              y1="220"
              x2="675"
              y2="220"
              stroke="var(--text-muted)"
            />

            <text
              x="18"
              y="18"
              fill="var(--text-secondary)"
              fontSize="12"
            >
              Price (₹)
            </text>

            <text
              x="80"
              y="248"
              fill="var(--text-secondary)"
              fontSize="12"
            >
              Historical data
            </text>

            <text
              x="515"
              y="248"
              fill="var(--text-secondary)"
              fontSize="12"
            >
              Forecast period
            </text>

            <text
              x="350"
              y="112"
              textAnchor="middle"
              fill="var(--text-secondary)"
              fontSize="15"
            >
              Forecast chart preview
            </text>

            <text
              x="350"
              y="135"
              textAnchor="middle"
              fill="var(--text-muted)"
              fontSize="12"
            >
              Connect the Kronos API to display real predictions
            </text>
          </svg>
        </div>

        <div
          style={{
            display: 'flex',
            gap: 'var(--space-4)',
            flexWrap: 'wrap',
            fontSize: 12,
            color: 'var(--text-secondary)',
          }}
        >
          <span>Symbol: {symbol}</span>
          <span>Target: {target.toUpperCase()}</span>
          <span>Horizon: {horizon} candles</span>
          <span>Forecast date: {forecastDate || 'Not selected'}</span>
        </div>
      </div>
    </section>
  );
}