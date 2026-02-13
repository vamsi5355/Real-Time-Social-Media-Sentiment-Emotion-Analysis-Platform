import React from "react";

const DistributionChart = ({ distribution, loading = false }) => {
  if (loading) {
    return (
      <div className="distribution-chart">
        <p>Loading distribution...</p>
      </div>
    );
  }

  if (!distribution || distribution.total === 0) {
    return (
      <div className="distribution-chart">
        <p>No sentiment data available</p>
      </div>
    );
  }

  const total = distribution.total || 0;
  const positivePercentage = ((distribution.positive_count || 0) / total * 100).toFixed(1);
  const negativePercentage = ((distribution.negative_count || 0) / total * 100).toFixed(1);
  const neutralPercentage = ((distribution.neutral_count || 0) / total * 100).toFixed(1);

  return (
    <div className="distribution-chart">
      <h3>Sentiment Distribution</h3>
      <div className="chart-container">
        <div className="chart-bar">
          <div className="bar-segment positive" style={{ width: `${positivePercentage}%` }}>
            <span>{positivePercentage}%</span>
          </div>
          <div className="bar-segment negative" style={{ width: `${negativePercentage}%` }}>
            <span>{negativePercentage}%</span>
          </div>
          <div className="bar-segment neutral" style={{ width: `${neutralPercentage}%` }}>
            <span>{neutralPercentage}%</span>
          </div>
        </div>
      </div>
      <div className="chart-legend">
        <div className="legend-item">
          <span className="legend-color positive"></span>
          <span>Positive: {distribution.positive_count} ({positivePercentage}%)</span>
        </div>
        <div className="legend-item">
          <span className="legend-color negative"></span>
          <span>Negative: {distribution.negative_count} ({negativePercentage}%)</span>
        </div>
        <div className="legend-item">
          <span className="legend-color neutral"></span>
          <span>Neutral: {distribution.neutral_count} ({neutralPercentage}%)</span>
        </div>
      </div>
      <p className="chart-total">Total Posts: {total}</p>
    </div>
  );
};

export default DistributionChart;
