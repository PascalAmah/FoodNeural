import axios from "axios";

const API_BASE_URL = process.env.VITE_APP_URL || "http://localhost:5000";

// Create axios instance with default config
const api = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  timeout: 10000,
  headers: {
    "Content-Type": "application/json",
  },
});

export const getFoodImpact = async (foodName) => {
  try {
    const response = await api.get(`/impact/${encodeURIComponent(foodName)}`);
    return response.data;
  } catch (error) {
    console.error("Error fetching food impact data:", error);
    throw error;
  }
};

export const getRecommendations = async (foodName, useAI = true, limit = 3) => {
  try {
    const params = {
      use_ai: useAI.toString(),
      limit: limit.toString(),
      carbon_weight: "0.3",
      water_weight: "0.2",
      energy_weight: "0.1",
      waste_weight: "0.1",
      deforestation_weight: "0.3",
    };

    const response = await api.get(
      `/recommendations/${encodeURIComponent(foodName)}`,
      { params }
    );
    return response.data;
  } catch (error) {
    console.error("Error fetching recommendations:", error);
    throw error;
  }
};

export const searchFoods = async (query) => {
  try {
    const response = await api.get("/search", {
      params: { q: query },
    });
    return Array.isArray(response.data) ? response.data : [];
  } catch (error) {
    console.error("Error searching foods:", error);
    return [];
  }
};
