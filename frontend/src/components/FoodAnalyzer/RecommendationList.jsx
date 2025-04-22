import React from "react";
import { motion as Motion } from "framer-motion";

const formatImpactValue = (value, unit) => {
  // Convert string values to numbers if possible
  const numValue = typeof value === "string" ? parseFloat(value) : value;

  // Check for valid number
  if (numValue === null || numValue === undefined || isNaN(numValue)) {
    console.log(`Invalid value received: ${value}`);
    return "N/A";
  }

  // Format number with appropriate decimal places
  const formattedValue = Number(numValue).toLocaleString(undefined, {
    minimumFractionDigits: 0,
    maximumFractionDigits: 1,
  });

  return `${formattedValue} ${unit}`;
};

const ImpactMetrics = ({ impact }) => {
  // Check if impact exists and has either breakdown or direct values
  if (!impact) return null;

  // Get values from either breakdown or direct properties
  const values = {
    water: impact.breakdown?.water ?? impact.water,
    carbon: impact.breakdown?.carbon ?? impact.carbon,
    energy: impact.breakdown?.energy ?? impact.energy,
  };

  return (
    <div className="mt-2 text-sm text-gray-500 space-y-1">
      <p>Water usage: {formatImpactValue(values.water, "L")}</p>
      <p>Carbon footprint: {formatImpactValue(values.carbon, "kg CO₂")}</p>
      {values.energy && (
        <p>Energy usage: {formatImpactValue(values.energy, "MJ")}</p>
      )}
    </div>
  );
};

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
      className="bg-white md:p-6 md:rounded-xl md:shadow-lg font-montserrat"
    >
      <h2 className="text-lg md:text-xl font-semibold mb-4 font-lora">
        Sustainable Alternatives
      </h2>
      <ul className="space-y-4">
        {recommendations.map((rec, index) => (
          <Motion.li
            key={index}
            variants={itemVariants}
            className="p-3 md:p-4 bg-green-50 rounded-lg hover:bg-green-100 cursor-pointer 
              transition-colors duration-200"
          >
            <h3
              className="font-medium text-base md:text-lg text-green-800 font-lora"
              onClick={() => onSelectRecommendation(rec.name)}
            >
              {rec.name}
            </h3>
            {rec.sustainability_improvement && (
              <p className="text-green-600 mt-1">
                {rec.sustainability_improvement}% more sustainable
              </p>
            )}
            {rec.explanation && (
              <p className="text-gray-600 mt-2 text-sm">{rec.explanation}</p>
            )}
            <ImpactMetrics impact={rec.impact} />
          </Motion.li>
        ))}
      </ul>
      <p className="text-xs md:text-sm text-gray-500 mt-4">
        Click on an alternative to analyze its impact
      </p>
    </Motion.div>
  );
};

export default RecommendationsList;
