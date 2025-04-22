import React from "react";

const About = () => {
  return (
    <section
      id="about"
      className="py-8 sm:py-12 md:py-16 px-4 sm:px-8 md:px-16 bg-white overflow-x-hidden"
      data-aos="fade-up"
    >
      <div className="container mx-auto max-w-7xl">
        <h2
          className="text-2xl sm:text-3xl md:text-4xl font-bold text-green-600 mb-6 sm:mb-8 text-center font-primary"
          data-aos="fade-down"
          data-aos-delay="100"
        >
          About
        </h2>

        <div className="grid lg:grid-cols-2 gap-6 sm:gap-8 md:gap-12 items-center">
          <div
            className="order-2 md:order-1"
            data-aos="fade-right"
            data-aos-delay="200"
          >
            <img
              src="/about_img.PNG"
              alt="Food Impact Analysis"
              className="rounded-lg shadow-lg w-full h-auto"
              loading="lazy"
            />
          </div>

          <div
            className="order-1 md:order-2 space-y-4 sm:space-y-6"
            data-aos="fade-left"
            data-aos-delay="300"
          >
            <p className="text-base sm:text-lg text-gray-700 font-secondary">
              Food choices impact the planet more than we realize. From carbon
              emissions to water consumption, every meal contributes to our
              environmental footprint.
            </p>
            <p className="text-base sm:text-lg text-gray-700 font-secondary">
              FoodNeural helps you understand and reduce that impact using
              AI-powered analysis. By evaluating the sustainability of different
              foods, we empower individuals and businesses to make smarter,
              greener choices.
            </p>

            <div className="bg-green-50 p-4 sm:p-6 rounded-lg border border-green-100">
              <h3 className="text-lg sm:text-xl font-semibold text-green-700 mb-2 sm:mb-3 font-primary">
                🌍 Our Mission
              </h3>
              <p className="text-sm sm:text-base text-gray-700 font-secondary">
                To provide data-driven insights that promote sustainable eating
                and help reduce the environmental impact of food production.
              </p>
            </div>

            <div className="bg-green-50 p-4 sm:p-6 rounded-lg border border-green-100">
              <h3 className="text-lg sm:text-xl font-semibold text-green-700 mb-2 sm:mb-3 font-primary">
                💡 How We Do It
              </h3>
              <p className="text-sm sm:text-base text-gray-700 font-secondary">
                Using machine learning and scientific food databases, we analyze
                the environmental footprint of ingredients, providing users with
                sustainability scores and eco-friendly alternatives.
              </p>
            </div>

            <p className="text-base sm:text-lg font-medium text-green-600 font-secondary">
              Join us in building a more sustainable future, one meal at a time!
              🌱✨
            </p>

            <div className="flex gap-4 mt-4">
              <a
                href="https://github.com/PascalAmah/FoodNeural"
                className="text-green-600 hover:text-green-800 transition-colors"
                target="_blank"
                rel="noopener noreferrer"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="28"
                  height="28"
                  viewBox="0 0 24 24"
                  fill="currentColor"
                >
                  <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
                </svg>
              </a>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default About;
