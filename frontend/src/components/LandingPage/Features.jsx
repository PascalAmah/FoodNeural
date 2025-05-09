import React, { useEffect } from "react";
import { motion as Motion } from "framer-motion";
import { Card, CardContent } from "../Card";
import AOS from "aos";

const Features = () => {
  useEffect(() => {
    AOS.init({
      duration: 1000,
      once: true,
      offset: 100,
      easing: "ease-out-cubic",
    });
  }, []);

  const features = [
    {
      name: "🌱 AI-Powered Food Analysis",
      description:
        "Instantly evaluate the environmental impact of any food item using machine learning and sustainability data.",
      image: "/feature_1.PNG",
    },
    {
      name: "📊 Carbon Footprint Tracking",
      description:
        "Get insights into the CO₂ emissions associated with food production, helping you make greener choices.",
      image: "/feature_2.PNG",
    },
    {
      name: "💧 Water Usage Assessment",
      description:
        "Understand how much water is required to produce different foods and discover more sustainable alternatives.",
      image: "/feature_3.PNG",
    },
    {
      name: "🌍 Sustainability Score",
      description:
        "Receive a comprehensive sustainability rating based on multiple environmental factors.",
      image: "/feature_4.PNG",
    },
    {
      name: "🔄 Alternative Suggestions",
      description:
        "Get recommendations for lower-impact food choices without compromising nutrition or taste.",
      image: "/feature_5.PNG",
    },
  ];

  return (
    <section
      id="features"
      className="py-8 sm:py-12 md:py-16 px-4 sm:px-8 md:px-16 bg-gray-50 overflow-hidden"
      data-aos="fade-up"
      data-aos-duration="800"
    >
      <div className="container mx-auto max-w-6xl">
        <h2
          className="text-2xl sm:text-3xl md:text-4xl font-bold text-center text-green-600 mb-8 sm:mb-12 font-primary"
          data-aos="fade-down"
          data-aos-duration="800"
          data-aos-delay="100"
        >
          Our Features
        </h2>
        <div className="flex flex-col space-y-8">
          {features.map((feature, index) => (
            <Motion.div
              key={index}
              whileHover={{ y: -5 }}
              className="w-full transform transition-all duration-300"
              data-aos="fade-up"
              data-aos-duration="800"
              data-aos-delay={150 * (index + 1)}
              data-aos-anchor-placement="top-bottom"
            >
              <Card className="overflow-hidden hover:shadow-xl bg-white">
                <div className="grid md:grid-cols-2 gap-0">
                  <div
                    className={`h-40 sm:h-48 md:h-56 ${
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
                  <CardContent className="flex items-center p-4 sm:p-6 md:p-8">
                    <div>
                      <h3 className="text-lg sm:text-xl font-semibold mb-2 sm:mb-3 text-gray-800 font-primary">
                        {feature.name}
                      </h3>
                      <p className="text-sm sm:text-base text-gray-600 font-secondary">
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
