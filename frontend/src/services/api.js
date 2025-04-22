import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_APP_URL || "http://localhost:5000";

console.log("API Base URL:", API_BASE_URL);

const api = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Add request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(
      `Request: ${config.method.toUpperCase()} ${config.baseURL}${config.url}`,
      config.params
    );
    return config;
  },
  (error) => {
    console.error("Request Error:", error);
    return Promise.reject(error);
  }
);

// Add response interceptor
api.interceptors.response.use(
  (response) => {
    console.log("Response:", response.status, response.data);
    return response;
  },
  (error) => {
    console.error(
      "Response Error:",
      error.response?.status,
      error.response?.data || error.message
    );
    return Promise.reject(error);
  }
);

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

    const config = {
      params,
      timeout: 25000,
    };

    try {
      const response = await api.get(
        `/recommendations/${encodeURIComponent(foodName)}`,
        config
      );
      return response.data;
    } catch (error) {
      // If timeout or server error, try once more with AI disabled
      if (
        (error.code === "ECONNABORTED" || error.response?.status >= 500) &&
        useAI === true
      ) {
        console.log("Retrying recommendation without AI...");
        const fallbackParams = {
          ...params,
          use_ai: "false",
        };
        const fallbackResponse = await api.get(
          `/recommendations/${encodeURIComponent(foodName)}`,
          { params: fallbackParams, timeout: 10000 }
        );
        return fallbackResponse.data;
      }
      throw error;
    }
  } catch (error) {
    console.error("Error fetching recommendations:", error);
    throw error;
  }
};

export const searchFoods = async (query) => {
  try {
    const response = await api.get("/search", {
      params: { q: query },
      timeout: 5000,
    });
    return Array.isArray(response.data) ? response.data : [];
  } catch (error) {
    console.error("Error searching foods:", error);
    return [];
  }
};
