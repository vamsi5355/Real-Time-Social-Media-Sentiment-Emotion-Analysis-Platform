export default function PostCard({ post }) {
  if (!post) return null;

  const colors = {
    positive: "#10b981",
    negative: "#ef4444",
    neutral: "#6b7280",
  };

  const sentimentLabel = post.sentiment_label || post.sentiment || "neutral";
  const emoji = sentimentLabel === "positive" ? "😊" : 
                 sentimentLabel === "negative" ? "😞" : "😐";

  const contentPreview = post.content 
    ? post.content.substring(0, 150) + (post.content.length > 150 ? "..." : "")
    : "No content";

  return (
    <div
      style={{
        background: "#fff",
        borderLeft: `4px solid ${colors[sentimentLabel] || "#9e9e9e"}`,
        padding: "12px",
        margin: "8px 0",
        borderRadius: "6px",
        boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
      }}
    >
      <div style={{ marginBottom: "8px" }}>
        <p style={{ margin: "0 0 8px 0", color: "#333" }}>
          <strong>📝 {contentPreview}</strong>
        </p>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px", fontSize: "0.9rem" }}>
        <div>
          <span>Sentiment: </span>
          <span style={{ fontWeight: "bold", color: colors[sentimentLabel] }}>
            {emoji} {sentimentLabel}
          </span>
        </div>
        {post.emotion && (
          <div>
            <span>Emotion: </span>
            <span style={{ fontWeight: "bold" }}>
              {post.emotion}
            </span>
          </div>
        )}
        {post.confidence_score !== undefined && (
          <div>
            <span>Confidence: </span>
            <span style={{ fontWeight: "bold" }}>
              {(post.confidence_score * 100).toFixed(1)}%
            </span>
          </div>
        )}
        {post.source && (
          <div>
            <span>Source: </span>
            <span style={{ fontWeight: "bold" }}>
              {post.source}
            </span>
          </div>
        )}
      </div>
    </div>
  );
}

