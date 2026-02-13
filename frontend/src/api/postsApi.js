import client from "./httpClient";

export const fetchPosts = async (limit = 10) => {
  const response = await client.get(`/api/posts?limit=${limit}`);
  return response.data;
};
