import { useState, useEffect } from "react";
import IntroPage from "@/components/IntroPage";
import SideNav from "@/components/SideNav";
import HeroSection from "@/components/HeroSection";
import HowItWorks from "@/components/HowItWorks";
import Features from "@/components/Features";
import Dashboard from "@/components/Dashboard";
import Impact from "@/components/Impact";
import Revenue from "@/components/Revenue";
import Contact from "@/components/Contact";

const Index = () => {
  const [showIntro, setShowIntro] = useState(true);

  useEffect(() => {
    // Enable smooth scrolling
    document.documentElement.style.scrollBehavior = "smooth";
    
    return () => {
      document.documentElement.style.scrollBehavior = "auto";
    };
  }, []);

  if (showIntro) {
    return <IntroPage onComplete={() => setShowIntro(false)} />;
  }

  return (
    <div className="min-h-screen bg-background text-foreground overflow-x-hidden">
      <SideNav />
      
      <main>
        <HeroSection />
        <HowItWorks />
        <Features />
        <Dashboard />
        <Impact />
        <Revenue />
        <Contact />
      </main>
    </div>
  );
};

export default Index;