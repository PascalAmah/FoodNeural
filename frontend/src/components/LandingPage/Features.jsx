import React from "react";
import { motion as Motion } from "framer-motion";
import { Card, CardContent } from "../Card";

const Features = () => {
  const features = [
    {
      name: "🌱 AI-Powered Food Analysis",
      description:
        "Instantly evaluate the environmental impact of any food item using machine learning and sustainability data.",
      image: "/api/placeholder/300/300",
    },
    {
      name: "📊 Carbon Footprint Tracking",
      description:
        "Get insights into the CO₂ emissions associated with food production, helping you make greener choices.",
      image: "/api/placeholder/300/300",
    },
    {
      name: "💧 Water Usage Assessment",
      description:
        "Understand how much water is required to produce different foods and discover more sustainable alternatives.",
      image: "/api/placeholder/300/300",
    },
    {
      name: "🌍 Sustainability Score",
      description:
        "Receive a comprehensive sustainability rating based on multiple environmental factors.",
      image: "/api/placeholder/300/300",
    },
    {
      name: "🔄 Alternative Suggestions",
      description:
        "Get recommendations for lower-impact food choices without compromising nutrition or taste.",
      image: "/api/placeholder/300/300",
    },
  ];

  return (
    <section
      className="py-8 sm:py-12 md:py-16 px-4 sm:px-8 md:px-16 bg-gray-50"
      data-aos="fade-up"
    >
      <div className="container mx-auto max-w-7xl">
        <h2
          className="text-2xl sm:text-3xl md:text-4xl font-bold text-center text-green-600 mb-8 sm:mb-12"
          data-aos="fade-down"
          data-aos-delay="100"
        >
          Our Features
        </h2>
        <div className="flex flex-col space-y-6 sm:space-y-8">
          {features.map((feature, index) => (
            <Motion.div
              key={index}
              whileHover={{ y: -5 }}
              className="w-full transform transition duration-300"
              data-aos="fade-up"
              data-aos-delay={200 + index * 100}
            >
              <Card className="overflow-hidden hover:shadow-xl">
                <div className="grid md:grid-cols-2 gap-0">
                  <div
                    className={`h-48 sm:h-64 md:h-full ${
                      index % 2 === 1 ? "md:order-2" : ""
                    }`}
                  >
                    <img
                      src={feature.image}
                      alt={feature.name}
                      className="w-full h-full object-cover"
                      loading="lazy"
                    />
                  </div>
                  <CardContent className="flex items-center p-6 sm:p-8 md:p-12">
                    <div>
                      <h3 className="text-lg sm:text-xl md:text-2xl font-semibold mb-3 sm:mb-4">
                        {feature.name}
                      </h3>
                      <p className="text-sm sm:text-base text-gray-600">
                        {feature.description}
                      </p>
                    </div>
                  </CardContent>
                </div>
              </Card>
            </Motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Features;
