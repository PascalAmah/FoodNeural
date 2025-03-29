import axios from "axios";

// Use a fixed base URL
// eslint-disable-next-line no-undef
const API_BASE_URL = `${process.env.VITE_API_URL}/api`;

export const getFoodImpact = async (foodName) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/impact/${foodName}`);
    return response.data;
  } catch (error) {
    console.error("Error fetching food impact data:", error);
    throw error;
  }
};

export const getRecommendations = async (foodName) => {
  try {
    const response = await axios.get(
      `${API_BASE_URL}/recommendations/${foodName}`
    );
    return response.data;
  } catch (error) {
    console.error("Error fetching recommendations:", error);
    throw error;
  }
};

export const searchFoods = async (query) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/search?q=${query}`);
    return response.data;
  } catch (error) {
    console.error("Error searching foods:", error);
    return [];
  }
};
