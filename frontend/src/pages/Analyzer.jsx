import React from "react";
import FoodAnalyzer from "../components/FoodAnalyzer/FoodAnalyzer";
import Navbar from "../components/LandingPage/Navbar";
import { motion as Motion } from "framer-motion";

const Analyzer = () => {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="fixed top-0 left-0 right-0 z-50">
        <Navbar isAnalyzerPage={true} />
      </header>

      <Motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className="flex-1 md:mt-20 mt-16"
      >
        <div className="bg-gradient-to-r from-green-500/80 to-[#FFA726]/70 text-white py-8 md:py-12 px-4">
          <div className="max-w-6xl mx-auto">
            <h1 className="text-2xl md:text-4xl font-bold tracking-tight font-primary">
              Food Sustainability Analyzer
            </h1>
            <p className="mt-2 md:mt-4 text-base md:text-lg text-green-50 font-secondary">
              Discover the environmental impact of your food choices
            </p>
          </div>
        </div>

        <main className="max-w-6xl mx-auto px-4 py-8">
          <FoodAnalyzer />
        </main>
      </Motion.div>

      <footer className="bg-gray-800 text-gray-300 py-6 text-center text-sm font-secondary">
        <div className="max-w-6xl mx-auto px-4">
          <p>© 2025 FoodNeural | Data sources: Open Food Facts, USDA, FAO</p>
        </div>
      </footer>
    </div>
  );
};

export default Analyzer;
