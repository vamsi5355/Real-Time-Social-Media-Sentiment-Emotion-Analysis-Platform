export default function StatsCard({ 
  title = "", 
  value = 0, 
  subtext = "",
  icon = "📊", 
  color = "default",
  loading = false,
  distribution = null 
}) {
  // Legacy support for distribution-based rendering
  if (distribution) {
    const { positive = 0, neutral = 0, negative = 0 } = distribution;
    return (
      <div
        style={{
          display: "flex",
          justifyContent: "space-around",
          background: "#eee",
          padding: "1rem",
          borderRadius: "8px",
          marginTop: "1rem",
        }}
      >
        <div>😊 Positive: <b>{positive}</b></div>
        <div>😐 Neutral: <b>{neutral}</b></div>
        <div>😡 Negative: <b>{negative}</b></div>
      </div>
    );
  }

  // New stats card rendering
  if (loading) {
    return (
      <div style={{
        padding: "1.5rem",
        background: "#f5f5f5",
        borderRadius: "8px",
        textAlign: "center",
        boxShadow: "0 2px 4px rgba(0,0,0,0.1)"
      }}>
        <p>Loading...</p>
      </div>
    );
  }

  const getBgColor = () => {
    switch(color) {
      case 'positive': return '#d4edda';
      case 'negative': return '#f8d7da';
      case 'neutral': return '#d1ecf1';
      default: return '#e7e7e7';
    }
  };

  const getBorderColor = () => {
    switch(color) {
      case 'positive': return '#28a745';
      case 'negative': return '#dc3545';
      case 'neutral': return '#17a2b8';
      default: return '#999';
    }
  };

  return (
    <div style={{
      padding: "1.5rem",
      background: getBgColor(),
      borderRadius: "8px",
      borderLeft: `4px solid ${getBorderColor()}`,
      boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
      minHeight: "120px",
      display: "flex",
      flexDirection: "column",
      justifyContent: "center"
    }}>
      <div style={{ fontSize: "2rem", marginBottom: "0.5rem" }}>
        {icon}
      </div>
      <div style={{ 
        fontSize: "0.9rem", 
        color: "#666", 
        marginBottom: "0.5rem" 
      }}>
        {title}
      </div>
      <div style={{ 
        fontSize: "2rem", 
        fontWeight: "bold",
        color: getBorderColor()
      }}>
        {value.toLocaleString()}
      </div>
      {subtext && (
        <div style={{ 
          fontSize: "0.85rem", 
          color: "#888",
          marginTop: "0.3rem"
        }}>
          {subtext}
        </div>
      )}
    </div>
  );
}
