import client from "./httpClient";

export const fetchSentimentDistribution = async (hours = 24) => {
  const response = await client.get("/api/sentiment/distribution", {
    params: { hours }
  });
  return response.data;
};

export const fetchSentimentStats = async () => {
  const response = await client.get("/api/sentiment/stats");
  return response.data;
};

export const fetchSentimentTrend = async (intervalMinutes = 5, periods = 12) => {
  const response = await client.get("/api/sentiment/trend", {
    params: {
      interval_minutes: intervalMinutes,
      periods: periods
    }
  });
  return response.data;
};

export const fetchAlerts = async (limit = 10) => {
  const response = await client.get("/api/alerts", {
    params: { limit }
  });
  return response.data;
};

export const checkAlerts = async () => {
  const response = await client.post("/api/alerts/check");
  return response.data;
};
