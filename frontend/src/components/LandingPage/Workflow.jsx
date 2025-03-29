import React from "react";
import { useNavigate } from "react-router-dom";

const Workflow = () => {
  const navigate = useNavigate();
  // Workflow steps with icons, titles and descriptions
  const workflowSteps = [
    {
      icon: "🔍",
      title: "Search Food Item",
      description:
        "Enter the name of a food item (e.g., beef, rice, almonds) into the analyzer.",
    },
    {
      icon: "🧠",
      title: "AI Analyzes Impact",
      description:
        "The system processes the food data, calculating its carbon footprint, water usage, and sustainability score using AI and food data.",
    },
    {
      icon: "📊",
      title: "Get Insights",
      description:
        "View detailed impact metrics and sustainability ratings, helping you make informed food choices.",
    },
    {
      icon: "🌱",
      title: "Make Better Choices",
      description:
        "Receive recommendations for low-impact substitutes to reduce your environmental footprint.",
    },
  ];

  return (
    <section
      className="py-8 sm:py-12 md:py-16 px-4 sm:px-8 md:px-16"
      style={{ backgroundColor: "rgba(102, 187, 106, 0.05)" }}
      data-aos="fade-up"
    >
      <div className="container mx-auto max-w-7xl">
        <h2
          className="text-2xl sm:text-3xl md:text-4xl font-bold text-center text-gray-800 mb-4"
          data-aos="fade-down"
          data-aos-delay="100"
        >
          Workflow
        </h2>
        <p
          className="text-sm sm:text-base md:text-lg text-center text-gray-700 max-w-3xl mx-auto mb-8 sm:mb-12"
          data-aos="fade-up"
          data-aos-delay="200"
        >
          Understanding the environmental impact of what we eat has never been
          easier. AI recommendations and intuitive visualizations help
          individuals and businesses make smarter and greener food decisions.
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
          {workflowSteps.map((step, index) => (
            <div
              key={index}
              className="relative p-[1px] rounded-lg bg-gradient-to-br from-orange-500 to-green-500"
              data-aos="zoom-in"
              data-aos-delay={300 + index * 100}
            >
              <div className="bg-white rounded-lg p-4 sm:p-6 h-full">
                <div
                  className="w-10 h-10 sm:w-12 sm:h-12 rounded-lg flex items-center justify-center mb-4"
                  style={{ backgroundColor: "rgba(102, 187, 106, 0.05)" }}
                >
                  <span
                    className="text-xl sm:text-2xl"
                    role="img"
                    aria-label={step.title}
                  >
                    {step.icon}
                  </span>
                </div>
                <h3 className="text-lg sm:text-xl font-semibold text-gray-800 mb-2 sm:mb-3">
                  {step.title}
                </h3>
                <p className="text-sm sm:text-base text-gray-600">
                  {step.description}
                </p>
              </div>
            </div>
          ))}
        </div>

        <div className="text-center mt-8 sm:mt-12">
          <button
            onClick={() => navigate("/analyzer")}
            className="bg-green-600 hover:bg-green-700 text-white font-medium py-2.5 sm:py-3 px-5 sm:px-6 
              rounded-lg transition-colors text-sm sm:text-base"
          >
            Try Our Analyzer
          </button>
        </div>
      </div>
    </section>
  );
};

export default Workflow;
