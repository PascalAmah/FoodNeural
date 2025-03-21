import React from "react";
import { motion as Motion } from "framer-motion";

const RecommendationsList = ({ recommendations, onSelectRecommendation }) => {
  if (!recommendations || recommendations.length === 0) return null;

  const listVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
  };

  return (
    <Motion.div
      initial="hidden"
      animate="visible"
      variants={listVariants}
      className="bg-white p-6 rounded-xl shadow-lg"
    >
      <h2 className="text-xl font-semibold mb-4">Sustainable Alternatives</h2>
      <ul className="space-y-4">
        {recommendations.map((rec, index) => (
          <Motion.li
            key={index}
            variants={itemVariants}
            className="p-4 bg-green-50 rounded-lg hover:bg-green-100 cursor-pointer 
              transition-colors duration-200"
            onClick={() => onSelectRecommendation(rec.name)}
          >
            <h3 className="font-medium text-lg text-green-800">{rec.name}</h3>
            {rec.sustainability_improvement && (
              <p className="text-green-600 mt-1">
                {rec.sustainability_improvement}% more sustainable
              </p>
            )}
            {rec.explanation && (
              <p className="text-gray-600 mt-2 text-sm">{rec.explanation}</p>
            )}
            {rec.impact && (
              <div className="mt-2 text-sm text-gray-500">
                <p>Water usage: {rec.impact.water_usage || "N/A"}</p>
                <p>Carbon footprint: {rec.impact.carbon_footprint || "N/A"}</p>
              </div>
            )}
          </Motion.li>
        ))}
      </ul>
      <p className="text-sm text-gray-500 mt-4">
        Click on an alternative to analyze its impact
      </p>
    </Motion.div>
  );
};

export default RecommendationsList;
