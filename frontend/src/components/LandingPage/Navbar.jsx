import { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { HiMenuAlt3, HiX } from "react-icons/hi";
import { motion as Motion } from "framer-motion";

const Navbar = () => {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const isAnalyzerPage = location.pathname === "/analyzer";

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const scrollToSection = (sectionId) => {
    const element = document.getElementById(sectionId);
    if (element) {
      const offset = 80;
      const elementPosition = element.getBoundingClientRect().top;
      const offsetPosition = elementPosition + window.pageYOffset - offset;

      window.scrollTo({
        top: offsetPosition,
        behavior: "smooth",
      });
      setIsMenuOpen(false);
    }
  };

  return (
    <nav
      className={`
        fixed top-0 left-0 right-0 z-50
        flex items-center
        px-4 lg:px-16 py-2.5 h-[70px] md:h-[80px] w-full
        transition-all duration-300 font-primary
        ${isScrolled ? "bg-white shadow-lg" : "bg-transparent"}
      `}
    >
      {/* Logo */}
      <button
        onClick={() =>
          isAnalyzerPage ? navigate("/") : scrollToSection("hero")
        }
        className="flex-none"
      >
        <img
          src="/logo.svg"
          alt="Logo"
          className="w-[120px] md:w-[160px] h-[35px] md:h-[45px] object-contain"
        />
      </button>

      {/* Desktop Navigation */}
      {!isAnalyzerPage && (
        <>
          {/* Center Nav Links */}
          <div className="hidden lg:flex items-center justify-center flex-1">
            <div className="flex items-center space-x-8">
              <button
                onClick={() => scrollToSection("features")}
                className="text-medium font-medium text-black hover:text-green-500 transition-colors"
              >
                Features
              </button>
              <button
                onClick={() => scrollToSection("about")}
                className="text-medium font-medium text-black hover:text-green-500 transition-colors"
              >
                About
              </button>
              <button
                onClick={() => scrollToSection("workflow")}
                className="text-medium font-medium text-black hover:text-green-500 transition-colors"
              >
                Workflow
              </button>
              <button
                onClick={() => scrollToSection("insights")}
                className="text-medium font-medium text-black hover:text-green-500 transition-colors"
              >
                Insights
              </button>
            </div>
          </div>

          {/* Get Started Button */}
          <button
            onClick={() => navigate("/analyzer")}
            className="hidden lg:block px-6 py-4 bg-green-500 hover:bg-green-600
              rounded-[14px] text-medium font-semibold text-white
              transition-colors"
          >
            Get Started
          </button>
        </>
      )}

      {/* Mobile & Tablet Menu Button */}
      {!isAnalyzerPage && (
        <button
          onClick={() => setIsMenuOpen(!isMenuOpen)}
          className="lg:hidden text-2xl ml-auto"
          aria-label="Toggle menu"
        >
          {isMenuOpen ? <HiX /> : <HiMenuAlt3 />}
        </button>
      )}

      {/* Mobile & Tablet Navigation Menu */}
      {!isAnalyzerPage && (
        <Motion.div
          initial={{ x: "-100%" }}
          animate={{ x: isMenuOpen ? 0 : "-100%" }}
          transition={{ type: "tween" }}
          className="fixed top-[70px] md:top-[80px] left-0 w-64 h-[calc(100vh-70px)] md:h-[calc(100vh-80px)] 
            bg-white shadow-xl lg:hidden"
        >
          <div className="flex flex-col p-6 gap-6">
            <button
              onClick={() => {
                scrollToSection("features");
                setIsMenuOpen(false);
              }}
              className="text-sm md:text-base font-medium text-black hover:text-green-500 transition-colors"
            >
              Features
            </button>
            <button
              onClick={() => {
                scrollToSection("about");
                setIsMenuOpen(false);
              }}
              className="text-sm md:text-base font-medium text-black hover:text-green-500 transition-colors"
            >
              About
            </button>
            <button
              onClick={() => {
                scrollToSection("workflow");
                setIsMenuOpen(false);
              }}
              className="text-sm md:text-base font-medium text-black hover:text-green-500 transition-colors"
            >
              Workflow
            </button>
            <button
              onClick={() => {
                scrollToSection("insights");
                setIsMenuOpen(false);
              }}
              className="text-sm md:text-base font-medium text-black hover:text-green-500 transition-colors"
            >
              Insights
            </button>
            <button
              onClick={() => {
                navigate("/analyzer");
                setIsMenuOpen(false);
              }}
              className="px-6 py-4 bg-green-500 hover:bg-green-600
                rounded-[14px] text-sm md:text-base font-semibold text-white
                transition-colors mt-4"
            >
              Get Started →
            </button>
          </div>
        </Motion.div>
      )}
    </nav>
  );
};

export default Navbar;
