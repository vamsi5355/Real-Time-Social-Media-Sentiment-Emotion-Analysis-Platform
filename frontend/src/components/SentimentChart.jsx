import React from "react";

const SentimentChart = ({ trend, loading = false }) => {
  if (loading) {
    return (
      <div className="sentiment-chart">
        <p>Loading trend...</p>
      </div>
    );
  }

  if (!trend || trend.length === 0) {
    return (
      <div className="sentiment-chart">
        <p>No trend data available</p>
      </div>
    );
  }

  const maxValue = Math.max(...trend.map(t => t.total || 0), 1);
  const chartHeight = 200;

  return (
    <div className="sentiment-chart">
      <h3>Sentiment Trend</h3>
      <div className="chart-container">
        <svg viewBox={`0 0 ${trend.length * 50} ${chartHeight}`} className="trend-chart">
          {/* Positive line */}
          <polyline
            points={trend.map((t, i) => `${i * 50 + 25},${chartHeight - (t.positive || 0) / maxValue * chartHeight}`).join(" ")}
            fill="none"
            stroke="#10b981"
            strokeWidth="2"
          />
          
          {/* Negative line */}
          <polyline
            points={trend.map((t, i) => `${i * 50 + 25},${chartHeight - (t.negative || 0) / maxValue * chartHeight}`).join(" ")}
            fill="none"
            stroke="#ef4444"
            strokeWidth="2"
          />
          
          {/* Neutral line */}
          <polyline
            points={trend.map((t, i) => `${i * 50 + 25},${chartHeight - (t.neutral || 0) / maxValue * chartHeight}`).join(" ")}
            fill="none"
            stroke="#6b7280"
            strokeWidth="2"
          />
          
          {/* Data points */}
          {trend.map((t, i) => (
            <g key={i}>
              <circle
                cx={i * 50 + 25}
                cy={chartHeight - (t.positive || 0) / maxValue * chartHeight}
                r="3"
                fill="#10b981"
              />
              <circle
                cx={i * 50 + 25}
                cy={chartHeight - (t.negative || 0) / maxValue * chartHeight}
                r="3"
                fill="#ef4444"
              />
              <circle
                cx={i * 50 + 25}
                cy={chartHeight - (t.neutral || 0) / maxValue * chartHeight}
                r="3"
                fill="#6b7280"
              />
            </g>
          ))}
        </svg>
      </div>
      <div className="chart-legend">
        <div className="legend-item">
          <span className="legend-color" style={{ backgroundColor: "#10b981" }}></span>
          <span>Positive</span>
        </div>
        <div className="legend-item">
          <span className="legend-color" style={{ backgroundColor: "#ef4444" }}></span>
          <span>Negative</span>
        </div>
        <div className="legend-item">
          <span className="legend-color" style={{ backgroundColor: "#6b7280" }}></span>
          <span>Neutral</span>
        </div>
      </div>
    </div>
  );
};

export default SentimentChart;
