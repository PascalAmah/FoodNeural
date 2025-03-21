import React from "react";
import FoodAnalyzer from "./components/FoodAnalyzer";
import { motion as Motion } from "framer-motion";

const App = () => {
  return (
    <div className="min-h-screen flex flex-col">
      <Motion.header
        initial={{ y: -50 }}
        animate={{ y: 0 }}
        className="bg-green-600 text-white p-6 shadow-lg"
      >
        <div className="max-w-6xl mx-auto">
          <h1 className="text-3xl font-bold">Food Sustainability Analyzer</h1>
          <p className="mt-2 opacity-90">
            Discover the environmental impact of your food choices
          </p>
        </div>
      </Motion.header>
      <main className="flex-1 py-8">
        <FoodAnalyzer />
      </main>
      <footer className="bg-gray-200 py-4 text-center text-gray-600 text-sm">
        <p>© 2025 FoodNeural | Data sources: Open Food Facts, USDA, FAO</p>
      </footer>
    </div>
  );
};

export default App;
