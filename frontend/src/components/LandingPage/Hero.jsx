import React from "react";
import { useNavigate } from "react-router-dom";

const Hero = () => {
  const navigate = useNavigate();

  return (
    <div
      className="min-h-screen w-full bg-cover bg-center"
      style={{
        backgroundImage: "url('/bg-gradient.png')",
      }}
    >
      <div className="flex items-center justify-center px-4 sm:px-6 md:px-8 py-16 sm:py-16 md:py-22">
        <div className="container mx-auto max-w-screen-xl text-center">
          <div className="flex flex-col items-center justify-center space-y-8 md:space-y-6">
            {/* Text Content */}
            <div className="w-full px-4 sm:px-6 md:px-8">
              <h1
                className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-bold mb-4 sm:mb-6 text-gray-800 pt-6 lg:pt-10 font-primary leading-tight"
                data-aos="fade-down"
                data-aos-delay="100"
              >
                Empower Your Choices with{" "}
                <span className="text-orange-500 mt-2">FoodNeural's </span>
                AI Insights
              </h1>
              <p
                className="text-base sm:text-lg md:text-xl lg:text-2xl text-gray-600 mb-6 sm:mb-8 max-w-3xl mx-auto font-secondary"
                data-aos="fade-up"
                data-aos-delay="200"
              >
                "Discover the environmental impact of your food choices, explore
                sustainable alternatives, and make smarter, eco-friendly
                decisions with the power of AI."
              </p>
              <div
                className="flex flex-col sm:flex-row items-center justify-center gap-4 sm:gap-6"
                data-aos="fade-up"
                data-aos-delay="300"
              >
                <button
                  onClick={() => navigate("/analyzer")}
                  className="w-full sm:w-auto px-6 py-3 sm:py-4 bg-green-500 hover:bg-green-600 
                  rounded-[14px] text-base sm:text-medium font-semibold text-white 
                  transition-all duration-300 hover:scale-105 active:scale-95 font-primary"
                >
                  Analyze →
                </button>
                <button
                  className="w-full sm:w-auto border text-gray-700 
                  hover:bg-gray-150 font-bold py-3 sm:py-4 px-6 rounded-[14px] 
                  transition-all duration-300 hover:scale-105 active:scale-95 font-primary"
                >
                  Learn More
                </button>
              </div>
            </div>

            {/* Dashboard Image */}
            <div
              className="w-full px-4 sm:px-6 md:px-8 mt-4 sm:mt-8"
              data-aos="zoom-in"
              data-aos-delay="400"
            >
              <div className="relative w-full max-w-5xl mx-auto">
                <picture>
                  <source
                    srcSet="/insights_mobile.png"
                    media="(max-width: 640px)"
                  />
                  <img
                    src="/insights.png"
                    alt="FoodNeural Dashboard"
                    className="w-full h-auto transition-transform duration-300 hover:scale-105"
                    loading="lazy"
                  />
                </picture>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Hero;
