import React, { useState, useRef, useEffect } from "react";
import {
  getFoodImpact,
  getRecommendations,
  searchFoods,
} from "../../services/api";
import ImpactChart from "./ImpactChart";
import RecommendationsList from "./RecommendationList";
import { motion as Motion } from "framer-motion";
import { IoClose } from "react-icons/io5";
import ErrorBoundary from "../ErrorBoundary";

const FoodAnalyzer = () => {
  const [query, setQuery] = useState("");
  const [impactData, setImpactData] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [foodInfo, setFoodInfo] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const inputRef = useRef(null);
  const suggestionsRef = useRef(null);

  const handleSearchWithValue = async (value) => {
    if (!value.trim()) {
      setError("Please enter a food name (e.g., Almond Milk, Beef)");
      return;
    }

    setShowSuggestions(false);
    setSuggestions([]);
    setIsLoading(true);
    setError("");
    setImpactData(null);
    setFoodInfo(null);
    setRecommendations([]);

    try {
      const [impactResult, recommendationsResult] = await Promise.all([
        getFoodImpact(value),
        getRecommendations(value),
      ]);

      // Validate and normalize impact data
      if (!impactResult || !validateImpactData(impactResult)) {
        throw new Error("Invalid impact data format");
      }

      // Normalize the data structure
      const normalizedImpactData = normalizeImpactData(impactResult);

      setImpactData(normalizedImpactData);

      // Store both alternatives and food info if available
      if (recommendationsResult) {
        setRecommendations(recommendationsResult.alternatives || []);

        // If we have food type info, store it
        if (recommendationsResult.food_info) {
          setFoodInfo(recommendationsResult.food_info);
          // Update the query to match the proper food name if available
          if (recommendationsResult.food_info.name) {
            setQuery(recommendationsResult.food_info.name);
          }
        }
      }
    } catch (err) {
      console.error("Search error:", err);
      setError(
        err.message === "Invalid impact data format"
          ? "Unable to analyze this food item's impact data."
          : "An error occurred while fetching data. Please try again."
      );
      setImpactData(null);

      // Still try to get recommendations even if impact data fails
      try {
        const recommendationsResult = await getRecommendations(value);
        setRecommendations(recommendationsResult.alternatives || []);

        // If we have food type info, store it
        if (recommendationsResult.food_info) {
          setFoodInfo(recommendationsResult.food_info);
          // Update the query to match the proper food name if available
          if (recommendationsResult.food_info.name) {
            setQuery(recommendationsResult.food_info.name);
          }
        }
      } catch (recErr) {
        console.error("Recommendations error:", recErr);
        setRecommendations([]);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const validateImpactData = (data) => {
    try {
      // First check if data exists
      if (!data || typeof data !== "object") return false;

      // If data comes with breakdown structure
      if (data.breakdown) {
        return (
          typeof data.food === "string" &&
          data.breakdown &&
          typeof data.breakdown.carbon === "number" &&
          typeof data.breakdown.water === "number" &&
          typeof data.breakdown.energy === "number" &&
          typeof data.breakdown.waste === "number" &&
          typeof data.breakdown.deforestation === "number"
        );
      }

      // If data comes with flat structure
      return (
        typeof data.food === "string" &&
        typeof data.carbon === "number" &&
        typeof data.water === "number" &&
        typeof data.energy === "number" &&
        typeof data.waste === "number" &&
        typeof data.deforestation === "number"
      );
    } catch {
      return false;
    }
  };

  // Add this function to normalize the data structure
  const normalizeImpactData = (data) => {
    if (!data) return null;

    if (data.breakdown) return data;

    // Converts flat structure to breakdown structure
    return {
      food: data.food,
      score: data.environmental_score || 5,
      breakdown: {
        carbon: data.carbon,
        water: data.water,
        energy: data.energy,
        waste: data.waste,
        deforestation: data.deforestation,
      },
      impact: data.impact,
      ingredients: [],
      certifications: [],
      nutrition: {
        protein: 0,
        fat: 0,
        carbs: 0,
        fiber: 0,
      },
    };
  };

  const handleSearch = () => handleSearchWithValue(query);

  const handleInputChange = async (e) => {
    const value = e.target.value;
    setQuery(value);

    if (error) setError("");

    if (!isLoading && value.trim().length > 1) {
      try {
        const results = await searchFoods(value);
        setSuggestions(results);
        setShowSuggestions(true);
      } catch {
        setSuggestions([]);
        setShowSuggestions(false);
      }
    } else {
      setSuggestions([]);
      setShowSuggestions(false);
    }
  };

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        inputRef.current &&
        !inputRef.current.contains(event.target) &&
        suggestionsRef.current &&
        !suggestionsRef.current.contains(event.target)
      ) {
        setShowSuggestions(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  const selectSuggestion = (suggestion) => {
    setQuery(suggestion);
    setSuggestions([]);
    setShowSuggestions(false);
    handleSearchWithValue(suggestion);
  };

  const handleSelectRecommendation = (food) => {
    setQuery(food);
    handleSearchWithValue(food);
  };

  const handleClearSearch = () => {
    setQuery("");
    setImpactData(null);
    setRecommendations([]);
    setFoodInfo(null);
    setError("");
    setSuggestions([]);
    setShowSuggestions(false);
    inputRef.current?.focus();
  };

  const formatNutritionValue = (value, unit = "g") => {
    if (typeof value !== "number") return `0${unit}`;
    return `${value.toFixed(1)}${unit}`;
  };

  return (
    <div className="max-w-6xl font-montserrat">
      <Motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5 }}
        className="bg-white md:p-8 p-5 rounded-2xl shadow-xl"
      >
        <div className="relative">
          <div
            className={`flex flex-col sm:flex-row gap-4 ${
              impactData || recommendations.length > 0 ? "mb-6" : ""
            }`}
          >
            <div className="flex-1 relative">
              <div className="relative">
                <input
                  type="text"
                  ref={inputRef}
                  className="w-full p-3 pr-10 rounded-lg border border-gray-300 focus:border-green-500 
                    focus:ring-2 focus:ring-green-200 outline-none transition-all duration-200 font-montserrat"
                  placeholder="Enter food name (e.g., Almond Milk, Beef)"
                  value={query}
                  onChange={handleInputChange}
                  onKeyDown={(e) => e.key === "Enter" && handleSearch()}
                  disabled={isLoading}
                  aria-label="Search for a food item"
                  aria-autocomplete="list"
                  aria-controls="suggestions-list"
                  aria-expanded={showSuggestions}
                />
                {query && !isLoading && (
                  <button
                    onClick={handleClearSearch}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                    aria-label="Clear search"
                  >
                    <IoClose size={20} />
                  </button>
                )}
              </div>
              {showSuggestions && suggestions.length > 0 && (
                <Motion.ul
                  ref={suggestionsRef}
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="absolute w-full bg-white border border-gray-200 rounded-lg shadow-lg 
                    mt-1 max-h-40 overflow-y-auto z-10"
                  id="suggestions-list"
                  role="listbox"
                >
                  {suggestions.map((suggestion, index) => (
                    <li
                      key={index}
                      className="p-3 hover:bg-gray-100 cursor-pointer"
                      onClick={() => selectSuggestion(suggestion)}
                      role="option"
                      aria-selected={false}
                    >
                      {suggestion}
                    </li>
                  ))}
                </Motion.ul>
              )}
            </div>
            <Motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className={`w-full sm:w-auto px-6 py-3 rounded-lg text-white text-medium font-semibold font-primary
                ${
                  isLoading
                    ? "bg-gray-400 cursor-not-allowed"
                    : "bg-green-600 hover:bg-green-700"
                }
                transition-colors duration-200`}
              onClick={handleSearch}
              disabled={isLoading}
              aria-label={
                isLoading ? "Analyzing in progress" : "Analyze food impact"
              }
            >
              {isLoading ? "Analyzing..." : "Analyze"}
            </Motion.button>
          </div>
        </div>

        {error && (
          <Motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-red-500 mb-4"
          >
            {error}
          </Motion.div>
        )}

        {/* Enhanced Food Information Card */}
        {foodInfo && (
          <Motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5 }}
            className="mb-6 p-5 bg-gray-50 rounded-lg border border-gray-200"
          >
            <div className="flex flex-col md:flex-row gap-6">
              {/* Food info section */}
              <div className="flex-1">
                <div className="flex items-center mb-3">
                  <h3 className="text-xl font-semibold mr-2">
                    {foodInfo.name}
                  </h3>
                  <span className="text-sm px-2 py-1 bg-green-100 text-green-800 rounded-full">
                    {foodInfo.type}
                  </span>
                  {foodInfo.source && (
                    <span className="ml-2 text-xs text-gray-500">
                      Source: {foodInfo.source}
                    </span>
                  )}
                </div>

                <p className="text-gray-700 mb-3">{foodInfo.description}</p>

                {foodInfo.details && (
                  <div className="mt-2">
                    <p className="text-gray-600 text-sm italic">
                      {foodInfo.details}
                    </p>
                  </div>
                )}
              </div>

              {/* Nutrition facts section */}
              {foodInfo.nutrition && (
                <div className="w-full md:w-72 bg-white border border-gray-200 rounded-lg p-4">
                  <h4 className="font-bold text-center border-b pb-2 mb-2">
                    Nutrition Facts
                  </h4>
                  <div className="text-sm">
                    {foodInfo.nutrition.calories && (
                      <div className="flex justify-between py-1 border-b">
                        <span>Calories</span>
                        <span>
                          {formatNutritionValue(
                            foodInfo.nutrition.calories,
                            "kcal"
                          )}
                        </span>
                      </div>
                    )}
                    <div className="flex justify-between py-1 border-b">
                      <span>Protein</span>
                      <span>
                        {formatNutritionValue(foodInfo.nutrition.protein, "g")}
                      </span>
                    </div>
                    <div className="flex justify-between py-1 border-b">
                      <span>Fat</span>
                      <span>
                        {formatNutritionValue(foodInfo.nutrition.fat, "g")}
                      </span>
                    </div>
                    <div className="flex justify-between py-1 border-b">
                      <span>Carbohydrates</span>
                      <span>
                        {formatNutritionValue(foodInfo.nutrition.carbs, "g")}
                      </span>
                    </div>
                    <div className="flex justify-between py-1">
                      <span>Fiber</span>
                      <span>
                        {formatNutritionValue(foodInfo.nutrition.fiber, "g")}
                      </span>
                    </div>
                  </div>
                  <div className="mt-2 text-xs text-gray-500 text-center">
                    Values per 100g
                  </div>
                </div>
              )}
            </div>
          </Motion.div>
        )}

        {(impactData || recommendations.length > 0) && (
          <Motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, ease: "easeOut" }}
            className="grid grid-cols-1 md:grid-cols-2 gap-6"
          >
            {impactData && (
              <ErrorBoundary>
                <ImpactChart impactData={impactData} />
              </ErrorBoundary>
            )}
            <RecommendationsList
              recommendations={recommendations}
              onSelectRecommendation={handleSelectRecommendation}
            />
          </Motion.div>
        )}
      </Motion.div>
    </div>
  );
};

export default FoodAnalyzer;
