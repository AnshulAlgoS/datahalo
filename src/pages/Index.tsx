import { useState, useEffect } from "react";
import IntroPage from "@/components/IntroPage";
import SideNav from "@/components/SideNav";
import HeroSection from "@/components/HeroSection";
import HowItWorks from "@/components/HowItWorks";
import Features from "@/components/Features";
import Impact from "@/components/Impact";
import Contact from "@/components/Contact";
import JournalistAnalyzer from "@/components/JournalistAnalyzer";
import News from "@/components/News";

const Index = () => {
  const [showIntro, setShowIntro] = useState(true);

  useEffect(() => {
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
        <JournalistAnalyzer />
        <News />
        <Impact />
        <Contact />
      </main>
    </div>
  );
};

export default Index;