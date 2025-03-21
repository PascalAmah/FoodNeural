// import React, { useState } from "react";
// import {
//   getFoodImpact,
//   getRecommendations,
//   searchFoods,
// } from "../services/api";
// import ImpactChart from "./ImpactChart";
// import RecommendationsList from "./RecommendationList";
// import { motion as Motion } from "framer-motion";

// const FoodAnalyzer = () => {
//   const [query, setQuery] = useState("");
//   const [impactData, setImpactData] = useState(null);
//   const [recommendations, setRecommendations] = useState([]);
//   const [isLoading, setIsLoading] = useState(false);
//   const [error, setError] = useState("");
//   const [suggestions, setSuggestions] = useState([]);
//   const [showSuggestions, setShowSuggestions] = useState(false);

//   const handleSearch = async () => {
//     if (!query.trim()) {
//       setError("Please enter a food name");
//       return;
//     }

//     setIsLoading(true);
//     setError("");
//     try {
//       // Fetch both impact data and recommendations in parallel
//       const [impactResult, recommendationsResult] = await Promise.all([
//         getFoodImpact(query),
//         getRecommendations(query),
//       ]);

//       setImpactData(impactResult);
//       setRecommendations(recommendationsResult.alternatives);
//     } catch {
//       setError("Could not find data for this food item.");
//       setImpactData(null);
//       // Still try to show recommendations even if impact data isn't found
//       try {
//         const recommendationsResult = await getRecommendations(query);
//         setRecommendations(recommendationsResult.alternatives);
//       } catch {
//         setRecommendations([]);
//       }
//     } finally {
//       setIsLoading(false);
//       setSuggestions([]);
//       setShowSuggestions(false);
//     }
//   };

//   const handleInputChange = async (e) => {
//     const value = e.target.value;
//     setQuery(value);

//     if (value.trim().length > 1) {
//       try {
//         const results = await searchFoods(value);
//         setSuggestions(results);
//         setShowSuggestions(true);
//       } catch {
//         setSuggestions([]);
//       }
//     } else {
//       setSuggestions([]);
//       setShowSuggestions(false);
//     }
//   };

//   const selectSuggestion = (suggestion) => {
//     setQuery(suggestion);
//     setSuggestions([]);
//     setShowSuggestions(false);
//   };

//   const handleSelectRecommendation = (food) => {
//     setQuery(food);
//     handleSearch();
//   };

//   return (
//     <div className="max-w-6xl mx-auto">
//       <Motion.div
//         initial={{ opacity: 0 }}
//         animate={{ opacity: 1 }}
//         transition={{ duration: 0.5 }}
//         className="bg-white p-8 rounded-2xl shadow-xl"
//       >
//         <div className="relative mb-6">
//           <div className="flex gap-4">
//             <div className="flex-1 relative">
//               <input
//                 type="text"
//                 className="w-full p-3 rounded-lg border border-gray-300 focus:border-green-500
//                   focus:ring-2 focus:ring-green-200 outline-none transition-all duration-200"
//                 placeholder="Enter food name (e.g., Almond Milk, Beef)"
//                 value={query}
//                 onChange={handleInputChange}
//                 onKeyDown={(e) => e.key === "Enter" && handleSearch()}
//               />
//               {showSuggestions && suggestions.length > 0 && (
//                 <Motion.ul
//                   initial={{ opacity: 0, y: -10 }}
//                   animate={{ opacity: 1, y: 0 }}
//                   className="absolute w-full bg-white border border-gray-200 rounded-lg shadow-lg
//                     mt-1 max-h-60 overflow-y-auto z-10"
//                 >
//                   {suggestions.map((suggestion, index) => (
//                     <li
//                       key={index}
//                       className="p-3 hover:bg-gray-100 cursor-pointer"
//                       onClick={() => selectSuggestion(suggestion)}
//                     >
//                       {suggestion}
//                     </li>
//                   ))}
//                 </Motion.ul>
//               )}
//             </div>
//             <Motion.button
//               whileHover={{ scale: 1.05 }}
//               whileTap={{ scale: 0.95 }}
//               className={`px-6 py-3 rounded-lg text-white font-medium
//                 ${
//                   isLoading
//                     ? "bg-gray-400 cursor-not-allowed"
//                     : "bg-green-600 hover:bg-green-700"
//                 }
//                 transition-colors duration-200`}
//               onClick={handleSearch}
//               disabled={isLoading}
//             >
//               {isLoading ? "Analyzing..." : "Analyze"}
//             </Motion.button>
//           </div>
//         </div>

//         {error && (
//           <Motion.div
//             initial={{ opacity: 0 }}
//             animate={{ opacity: 1 }}
//             className="text-red-500 mb-4"
//           >
//             {error}
//           </Motion.div>
//         )}

//         <div className="grid md:grid-cols-2 gap-6">
//           {impactData && <ImpactChart impactData={impactData} />}
//           <RecommendationsList
//             recommendations={recommendations}
//             onSelectRecommendation={handleSelectRecommendation}
//           />
//         </div>
//       </Motion.div>
//     </div>
//   );
// };

// export default FoodAnalyzer;

import React, { useState, useRef } from "react";
import {
  getFoodImpact,
  getRecommendations,
  searchFoods,
} from "../services/api";
import ImpactChart from "./ImpactChart";
import RecommendationsList from "./RecommendationList";
import { motion as Motion } from "framer-motion";
import { IoClose } from "react-icons/io5"; // Icon for clearing search

const FoodAnalyzer = () => {
  const [query, setQuery] = useState("");
  const [impactData, setImpactData] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const inputRef = useRef(null); // Ref for focusing input after clearing

  const handleSearch = async () => {
    if (!query.trim()) {
      setError("Please enter a food name (e.g., Almond Milk, Beef)");
      return;
    }

    // Immediately hide suggestions when Analyze is clicked
    setShowSuggestions(false);
    setSuggestions([]);

    setIsLoading(true);
    setError("");
    try {
      const [impactResult, recommendationsResult] = await Promise.all([
        getFoodImpact(query),
        getRecommendations(query),
      ]);

      if (!impactResult) {
        throw new Error("No impact data found");
      }

      setImpactData(impactResult);
      setRecommendations(recommendationsResult.alternatives || []);
    } catch (err) {
      setError(
        err.message === "No impact data found"
          ? "No environmental impact data found for this food item."
          : "An error occurred while fetching data. Please try again."
      );
      setImpactData(null);

      try {
        const recommendationsResult = await getRecommendations(query);
        setRecommendations(recommendationsResult.alternatives || []);
      } catch {
        setRecommendations([]);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = async (e) => {
    const value = e.target.value;
    setQuery(value);

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

  const selectSuggestion = (suggestion) => {
    setQuery(suggestion);
    setSuggestions([]);
    setShowSuggestions(false);
  };

  const handleSelectRecommendation = (food) => {
    setQuery(food);
    handleSearch();
  };

  const handleClearSearch = () => {
    setQuery("");
    setImpactData(null);
    setRecommendations([]);
    setError("");
    setSuggestions([]);
    setShowSuggestions(false);
    inputRef.current?.focus();
  };

  return (
    <div className="max-w-6xl mx-auto">
      <Motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5 }}
        className="bg-white p-8 rounded-2xl shadow-xl"
      >
        <div className="relative mb-6">
          <div className="flex gap-4">
            <div className="flex-1 relative">
              <div className="relative">
                <input
                  type="text"
                  ref={inputRef}
                  className="w-full p-3 pr-10 rounded-lg border border-gray-300 focus:border-green-500 
                    focus:ring-2 focus:ring-green-200 outline-none transition-all duration-200"
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
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="absolute w-full bg-white border border-gray-200 rounded-lg shadow-lg 
                    mt-1 max-h-60 overflow-y-auto z-10"
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
              className={`px-6 py-3 rounded-lg text-white font-medium
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

        <div className="grid md:grid-cols-2 gap-6">
          {impactData && <ImpactChart impactData={impactData} />}
          <RecommendationsList
            recommendations={recommendations}
            onSelectRecommendation={handleSelectRecommendation}
          />
        </div>
      </Motion.div>
    </div>
  );
};

export default FoodAnalyzer;
