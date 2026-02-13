import React, { useState, useEffect } from "react";
import { usePosts } from "../hooks/usePosts";
import { useWebSocket } from "../hooks/useWebSocket";
import { fetchSentimentDistribution, fetchSentimentTrend, fetchSentimentStats, fetchAlerts } from "../api/sentimentApi";
import Header from "../components/Header";
import PostCard from "../components/PostCard";
import StatsCard from "../components/StatsCard";
import DistributionChart from "../components/DistributionChart";
import SentimentChart from "../components/SentimentChart";
import "../App.css";

export default function Dashboard() {
  const { posts, loading, fetchPosts } = usePosts();
  const [distribution, setDistribution] = useState(null);
  const [trend, setTrend] = useState([]);
  const [stats, setStats] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [dataLoading, setDataLoading] = useState(true);
  const wsData = useWebSocket();

  useEffect(() => {
    const loadInitialData = async () => {
      try {
        setDataLoading(true);
        
        // Fetch all data in parallel
        const [dist, trendData, statsData, alertsData] = await Promise.all([
          fetchSentimentDistribution(24),
          fetchSentimentTrend(5, 12),
          fetchSentimentStats(),
          fetchAlerts(5)
        ]);

        setDistribution(dist);
        setTrend(trendData.trend || []);
        setStats(statsData);
        setAlerts(alertsData.alerts || []);

        // Fetch posts
        await fetchPosts();
      } catch (error) {
        console.error("Error loading dashboard data:", error);
      } finally {
        setDataLoading(false);
      }
    };

    loadInitialData();
  }, []);

  // Update stats when WebSocket data arrives
  useEffect(() => {
    if (wsData && wsData.data && wsData.data.stats) {
      setStats(wsData.data.stats);
      if (wsData.data.recent_alerts) {
        setAlerts(wsData.data.recent_alerts);
      }
    }
  }, [wsData]);

  const handleRefresh = async () => {
    setDataLoading(true);
    try {
      const [dist, trendData, statsData, alertsData] = await Promise.all([
        fetchSentimentDistribution(24),
        fetchSentimentTrend(5, 12),
        fetchSentimentStats(),
        fetchAlerts(5)
      ]);

      setDistribution(dist);
      setTrend(trendData.trend || []);
      setStats(statsData);
      setAlerts(alertsData.alerts || []);
    } catch (error) {
      console.error("Error refreshing data:", error);
    } finally {
      setDataLoading(false);
    }
  };

  if (loading && dataLoading) return <p>Loading dashboard...</p>;

  return (
    <div style={{ padding: "0" }}>
      <Header onRefresh={handleRefresh} />
      
      <div style={{ padding: "1rem", maxWidth: "1400px", margin: "0 auto" }}>
        {/* Top Stats Cards */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "1rem", marginBottom: "2rem" }}>
          <StatsCard
            title="Total Posts"
            value={stats?.total_count || 0}
            icon="📊"
            loading={dataLoading}
          />
          <StatsCard
            title="Positive"
            value={stats?.positive_count || 0}
            subtext={`${(stats?.positive_percentage || 0).toFixed(1)}%`}
            icon="😊"
            color="positive"
            loading={dataLoading}
          />
          <StatsCard
            title="Negative"
            value={stats?.negative_count || 0}
            subtext={`${(stats?.negative_percentage || 0).toFixed(1)}%`}
            icon="😞"
            color="negative"
            loading={dataLoading}
          />
          <StatsCard
            title="Neutral"
            value={stats?.neutral_count || 0}
            subtext={`${(stats?.neutral_percentage || 0).toFixed(1)}%`}
            icon="😐"
            color="neutral"
            loading={dataLoading}
          />
        </div>

        {/* Charts Row */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "2rem", marginBottom: "2rem" }}>
          <DistributionChart distribution={distribution} loading={dataLoading} />
          <SentimentChart trend={trend} loading={dataLoading} />
        </div>

        {/* Alerts Section */}
        {alerts && alerts.length > 0 && (
          <div style={{ marginBottom: "2rem", padding: "1rem", backgroundColor: "#fff3cd", borderRadius: "8px" }}>
            <h3>Recent Alerts</h3>
            <div style={{ display: "grid", gap: "0.5rem" }}>
              {alerts.map((alert, idx) => (
                <div key={idx} style={{ padding: "0.5rem", backgroundColor: "#fff", borderRadius: "4px" }}>
                  <span style={{ fontWeight: "bold" }}>{alert.alert_type}</span>
                  <span style={{ marginLeft: "1rem" }}>{alert.actual_value?.toFixed(2)}</span>
                  <span style={{ marginLeft: "1rem", color: "#666" }}>
                    {new Date(alert.triggered_at).toLocaleTimeString()}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Posts Section */}
        <div>
          <h3>🧵 Latest Posts</h3>
          {posts && posts.length > 0 ? (
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))", gap: "1rem" }}>
              {posts.slice(0, 6).map((p, i) => <PostCard key={i} post={p} />)}
            </div>
          ) : (
            <p>No posts available</p>
          )}
        </div>
      </div>
    </div>
  );
}