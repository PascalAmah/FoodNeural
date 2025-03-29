import Navbar from "../components/LandingPage/Navbar";
import Hero from "../components/LandingPage/Hero";
import Footer from "../components/LandingPage/Footer";
import Features from "../components/LandingPage/Features";
import About from "../components/LandingPage/About";
import TeamSection from "../components/LandingPage/Team";
import Workflow from "../components/LandingPage/Workflow";

const Home = () => {
  return (
    <div>
      <Navbar />
      <Hero />
      <Features />
      <About />
      <TeamSection />
      <Workflow />
      <Footer />
    </div>
  );
};

export default Home;
