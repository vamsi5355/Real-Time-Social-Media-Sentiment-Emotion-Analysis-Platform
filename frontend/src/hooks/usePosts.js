import { useEffect, useState } from "react";
import { fetchPosts as fetchPostsApi } from "../api/postsApi";

export const usePosts = () => {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchPosts = async (limit = 10) => {
    try {
      setLoading(true);
      const data = await fetchPostsApi(limit);
      setPosts(data.posts || []);
      return data.posts || [];
    } catch (err) {
      console.error("Failed to load posts", err);
      return [];
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPosts(10);
  }, []);

  return { posts, loading, fetchPosts };
};
