export default function Header({ onRefresh }) {
  return (
    <header style={{ 
      padding: "1rem", 
      background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)", 
      color: "white",
      display: "flex",
      justifyContent: "space-between",
      alignItems: "center"
    }}>
      <div>
        <h1 style={{ margin: 0, fontSize: "1.8rem" }}>
          📊 Real-Time Sentiment Dashboard
        </h1>
        <p style={{ margin: "0.3rem 0 0 0", fontSize: "0.9rem", opacity: 0.9 }}>
          Social Media Sentiment & Emotion Analysis Platform
        </p>
      </div>
      {onRefresh && (
        <button
          onClick={onRefresh}
          style={{
            padding: "0.6rem 1.2rem",
            background: "rgba(255,255,255,0.2)",
            border: "1px solid rgba(255,255,255,0.3)",
            color: "white",
            borderRadius: "6px",
            cursor: "pointer",
            fontSize: "1rem",
            transition: "all 0.3s ease"
          }}
          onMouseOver={(e) => {
            e.target.style.background = "rgba(255,255,255,0.3)";
            e.target.style.transform = "translateY(-2px)";
          }}
          onMouseOut={(e) => {
            e.target.style.background = "rgba(255,255,255,0.2)";
            e.target.style.transform = "translateY(0)";
          }}
        >
          🔄 Refresh
        </button>
      )}
    </header>
  );
}
