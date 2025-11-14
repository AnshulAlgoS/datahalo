import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Users, Eye } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useMemo } from "react";
import ThemeToggle from "@/components/ThemeToggle";
import heroBg from "@/assets/hero-bg.jpeg";

const HeroSection = () => {
  const navigate = useNavigate();
  
  const scrollToNext = () => {
    document.getElementById("how-it-works")?.scrollIntoView({ behavior: "smooth" });
  };

  // Generate random values once for sparkles
  const sparkleData = useMemo(() => 
    Array.from({ length: 12 }, () => ({
      leftOffset: (Math.random() - 0.5) * 100,
      xStart: (Math.random() - 0.5) * 50,
      xEnd: (Math.random() - 0.5) * 100,
      duration: 2 + Math.random() * 1,
      delay: Math.random() * 2,
    })),
    []
  );

  // Generate random values once for particles
  const particleData = useMemo(() =>
    Array.from({ length: 20 }, () => ({
      left: 45 + Math.random() * 10,
      top: 20 + Math.random() * 60,
      blur: Math.random() * 1.5,
      duration: 3 + Math.random() * 2,
      delay: Math.random() * 2,
    })),
    []
  );

  return (
    <section
      id="hero"
      className="relative min-h-screen flex flex-col items-center justify-center text-center overflow-hidden"
    >
      {/* Background image */}
      <div
        className="absolute inset-0 bg-cover bg-center"
        style={{
          backgroundImage: `url(${heroBg})`,
          opacity: 0.35,
        }}
      />

      {/* Gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-b from-background/60 via-background/80 to-background/95" />

      {/* 🗡️ CENTER BOTTOM-TO-TOP LIGHTNING SWORD - Main Feature */}
      {/* Main sword beam */}
      <motion.div
        className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[4px] h-full origin-bottom"
        style={{
          background: "linear-gradient(to top, hsl(191 100% 60%) 0%, hsl(191 100% 55%) 20%, hsl(210 100% 60%) 50%, hsl(210 90% 55%) 80%, transparent 100%)",
          boxShadow: "0 0 30px hsl(191 100% 60%), 0 0 60px hsl(191 100% 50% / 0.6), 0 0 90px hsl(191 100% 50% / 0.3)",
          filter: "brightness(1.5)",
        }}
        className="opacity-70 dark:opacity-100"
        animate={{
          scaleY: [0.85, 1, 0.85],
          opacity: [0.6, 1, 0.6],
        }}
        transition={{
          duration: 3,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />

      {/* Outer glow layer */}
      <motion.div
        className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[60px] h-full origin-bottom"
        style={{
          background: "linear-gradient(to top, hsl(191 100% 60% / 0.4) 0%, hsl(191 100% 55% / 0.3) 20%, hsl(210 95% 60% / 0.2) 50%, hsl(210 90% 55% / 0.15) 70%, transparent 100%)",
          filter: "blur(30px)",
        }}
        className="opacity-50 dark:opacity-80"
        animate={{
          scaleY: [0.9, 1.05, 0.9],
          opacity: [0.4, 0.8, 0.4],
        }}
        transition={{
          duration: 3.5,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />

      {/* Wide atmospheric glow */}
      <motion.div
        className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[150px] h-full origin-bottom"
        style={{
          background: "linear-gradient(to top, hsl(191 100% 60% / 0.3) 0%, hsl(191 95% 55% / 0.2) 25%, hsl(210 90% 60% / 0.15) 50%, transparent 75%)",
          filter: "blur(60px)",
        }}
        className="opacity-40 dark:opacity-70"
        animate={{
          scaleY: [0.95, 1.1, 0.95],
          scaleX: [1, 1.2, 1],
          opacity: [0.3, 0.7, 0.3],
        }}
        transition={{
          duration: 4,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />

      {/* Energy pulses traveling upward */}
      {[...Array(5)].map((_, i) => (
        <motion.div
          key={`pulse-${i}`}
          className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[8px] h-[80px] rounded-full opacity-60 dark:opacity-100"
          style={{
            background: "linear-gradient(to top, hsl(191 100% 70%) 0%, hsl(191 100% 60%) 50%, transparent 100%)",
            boxShadow: "0 0 20px hsl(191 100% 60% / 0.8)",
            filter: "blur(4px)",
          }}
          animate={{
            y: [0, -800],
            opacity: [0, 1, 1, 0],
            scaleY: [0.5, 1, 1, 0.5],
          }}
          transition={{
            duration: 3,
            repeat: Infinity,
            ease: "easeOut",
            delay: i * 0.6,
          }}
        />
      ))}

      {/* Bottom impact glow - where sword emerges */}
      <motion.div
        className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[300px] h-[150px]"
        style={{
          background: "radial-gradient(ellipse at center, hsl(191 100% 65% / 0.6) 0%, hsl(191 100% 60% / 0.4) 30%, hsl(210 95% 60% / 0.2) 60%, transparent 100%)",
          filter: "blur(50px)",
        }}
        className="opacity-50 dark:opacity-90"
        animate={{
          opacity: [0.4, 0.9, 0.4],
          scale: [0.95, 1.15, 0.95],
        }}
        transition={{
          duration: 2.5,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />

      {/* Sparkles around the sword */}
      {sparkleData.map((data, i) => (
        <motion.div
          key={`sparkle-${i}`}
          className="absolute bottom-[20%] left-1/2 w-[3px] h-[3px] rounded-full opacity-70 dark:opacity-100"
          style={{
            left: `calc(50% + ${data.leftOffset}px)`,
            background: i % 2 === 0 ? "hsl(191 100% 70%)" : "hsl(210 100% 70%)",
            boxShadow: "0 0 10px currentColor, 0 0 20px currentColor",
          }}
          animate={{
            y: [-50, -200],
            x: [data.xStart, data.xEnd],
            opacity: [0, 1, 0],
            scale: [0, 1.5, 0],
          }}
          transition={{
            duration: data.duration,
            repeat: Infinity,
            ease: "easeOut",
            delay: data.delay,
          }}
        />
      ))}

      {/* ⚡ Ambient cyan/blue atmosphere */}
      <motion.div
        className="absolute inset-0 opacity-[0.15] dark:opacity-[0.3]"
        style={{
          background: "radial-gradient(circle at 50% 50%, hsl(191 100% 60% / 0.3) 0%, transparent 60%)",
          filter: "blur(80px)",
        }}
        animate={{
          opacity: [0.15, 0.25, 0.15],
          scale: [1, 1.05, 1],
        }}
        transition={{
          duration: 6,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />

      {/* Main light beam - Cyan/Blue */}
      <motion.div
        className="absolute top-0 left-1/2 -translate-x-1/2 w-[300px] md:w-[500px] h-[600px]"
        style={{
          background: "linear-gradient(180deg, hsl(191 100% 60% / 0.2) 0%, hsl(210 90% 60% / 0.15) 40%, transparent 100%)",
          filter: "blur(60px)",
        }}
        animate={{
          opacity: [0.2, 0.35, 0.2],
          scaleY: [1, 1.1, 1],
        }}
        transition={{
          duration: 4,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />

      {/* Inner core beam */}
      <motion.div
        className="absolute top-0 left-1/2 -translate-x-1/2 w-[150px] md:w-[250px] h-[500px]"
        style={{
          background: "linear-gradient(180deg, hsl(191 100% 55% / 0.25) 0%, hsl(210 95% 60% / 0.15) 50%, transparent 100%)",
          filter: "blur(40px)",
        }}
        animate={{
          opacity: [0.25, 0.4, 0.25],
        }}
        transition={{
          duration: 3,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />

      {/* Core line */}
      <motion.div
        className="absolute top-0 left-1/2 -translate-x-1/2 w-[2px] h-[400px] opacity-30 dark:opacity-50"
        style={{
          background: "linear-gradient(180deg, hsl(191 100% 60%) 0%, hsl(210 100% 60%) 50%, transparent 100%)",
          boxShadow: "0 0 20px hsl(191 100% 60% / 0.4), 0 0 40px hsl(191 100% 60% / 0.2)",
        }}
        animate={{
          opacity: [0.3, 0.5, 0.3],
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />

      {/* Atmospheric glows - Cyan */}
      {[...Array(3)].map((_, i) => (
        <motion.div
          key={i}
          className="absolute top-0 left-1/2 -translate-x-1/2 w-[400px] md:w-[600px] h-[400px] opacity-10 dark:opacity-20"
          style={{
            background: `radial-gradient(ellipse at center, hsl(191 100% 55% / ${0.15 - i * 0.05}) 0%, transparent 70%)`,
            filter: "blur(60px)",
          }}
          animate={{
            opacity: [0.1, 0.2, 0.1],
            scale: [1, 1.15, 1],
          }}
          transition={{
            duration: 5 + i,
            repeat: Infinity,
            ease: "easeInOut",
            delay: i * 0.5,
          }}
        />
      ))}

      {/* Ground impact glow - Cyan */}
      <motion.div
        className="absolute top-[50%] left-1/2 -translate-x-1/2 w-[500px] md:w-[800px] h-[200px] opacity-15 dark:opacity-30"
        style={{
          background: "radial-gradient(ellipse at center, hsl(191 100% 60% / 0.3) 0%, hsl(210 90% 60% / 0.15) 40%, transparent 70%)",
          filter: "blur(80px)",
        }}
        animate={{
          opacity: [0.15, 0.3, 0.15],
          scaleX: [1, 1.1, 1],
        }}
        transition={{
          duration: 4,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />

      {/* Bottom ring glow */}
      <motion.div
        className="absolute top-[60%] left-1/2 -translate-x-1/2 w-[600px] md:w-[1000px] h-[100px] opacity-20 dark:opacity-35"
        style={{
          background: "radial-gradient(ellipse at center, hsl(191 100% 55% / 0.4) 0%, hsl(210 90% 60% / 0.2) 30%, transparent 70%)",
          filter: "blur(50px)",
        }}
        animate={{
          opacity: [0.2, 0.35, 0.2],
          scaleX: [1, 1.15, 1],
        }}
        transition={{
          duration: 3.5,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />

      {/* Light rays - Cyan */}
      {[...Array(8)].map((_, i) => (
        <motion.div
          key={i}
          className="absolute top-0 left-1/2 origin-top opacity-5 dark:opacity-15"
          style={{
            width: "2px",
            height: "500px",
            background: `linear-gradient(180deg, hsl(191 100% 60% / 0.3) 0%, transparent 100%)`,
            transform: `translateX(-50%) rotate(${i * 45}deg)`,
            filter: "blur(2px)",
          }}
          animate={{
            opacity: [0.05, 0.15, 0.05],
          }}
          transition={{
            duration: 3,
            repeat: Infinity,
            ease: "easeInOut",
            delay: i * 0.2,
          }}
        />
      ))}

      {/* Pulse effect - Cyan */}
      <motion.div
        className="absolute top-[40%] left-1/2 -translate-x-1/2 w-[100px] h-[100px] opacity-0"
        style={{
          background: "radial-gradient(circle, hsl(191 100% 60% / 0.4) 0%, transparent 70%)",
          filter: "blur(40px)",
        }}
        animate={{
          opacity: [0, 0.25, 0],
          scale: [0.5, 2, 0.5],
        }}
        transition={{
          duration: 4,
          repeat: Infinity,
          ease: "easeOut",
        }}
      />

      {/* Additional atmospheric particles - Cyan/Blue */}
      {particleData.map((data, i) => (
        <motion.div
          key={`particle-${i}`}
          className="absolute w-1 h-1 rounded-full opacity-30 dark:opacity-60"
          style={{
            left: `${data.left}%`,
            top: `${data.top}%`,
            background: i % 2 === 0 
              ? "hsl(191 100% 60%)" 
              : "hsl(210 90% 60%)",
            boxShadow: "0 0 10px currentColor",
            filter: `blur(${data.blur}px) brightness(1.3)`,
          }}
          animate={{
            y: [0, -100, 0],
            opacity: [0.3, 0.6, 0.3],
            scale: [1, 1.5, 1],
          }}
          transition={{
            duration: data.duration,
            repeat: Infinity,
            ease: "easeInOut",
            delay: data.delay,
          }}
        />
      ))}

      {/* Content */}
      <div className="relative z-10 px-6 max-w-5xl">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
        >
          <h1 className="font-orbitron text-5xl md:text-7xl lg:text-8xl font-bold mb-6 tracking-tight">
            <span className="bg-gradient-to-r from-primary via-secondary to-primary bg-clip-text text-transparent animate-glow-pulse">
              DataHalo
            </span>
          </h1>

          <h2 className="text-3xl md:text-5xl font-bold mb-4 text-foreground">
            AI-Powered Media Integrity
          </h2>
          <h3 className="text-xl md:text-2xl mb-8 text-muted-foreground">
            for Journalists
          </h3>

          <p className="text-lg md:text-xl text-muted-foreground max-w-3xl mx-auto mb-12 leading-relaxed">
            AI + NLP-backed verification of journalist authenticity.
            <br />
            <span className="text-primary font-semibold">
              Rebuilding Trust in Media — One Article at a Time.
            </span>
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Button
              size="lg"
              className="relative px-8 py-6 text-lg font-semibold bg-primary hover:bg-primary/90 text-primary-foreground rounded-xl overflow-hidden group"
            >
              <span className="relative z-10">View Demo</span>
              <div className="absolute inset-0 bg-gradient-to-r from-primary to-accent opacity-0 group-hover:opacity-100 transition-opacity" />
            </Button>

          </div>
        </motion.div>
      </div>

      {/* Top Right Buttons - View All Journalists & Narrative Analyzer */}
      <motion.div
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.6, delay: 0.3 }}
        className="absolute top-6 right-6 z-20 flex gap-3"
      >
        <ThemeToggle />
        <Button
          onClick={() => navigate("/narrative-analyzer")}
          className="group relative px-6 py-3 bg-card/50 backdrop-blur-md border border-border/50 hover:border-primary/50 text-foreground hover:text-primary rounded-xl transition-all duration-300 hover:shadow-[0_0_20px_rgba(0,200,255,0.4)]"
        >
          <Eye className="w-5 h-5 mr-2 inline-block transition-transform group-hover:scale-110" />
          <span className="font-semibold">Narrative Analyzer</span>
          
          {/* Glow effect on hover */}
          <div className="absolute inset-0 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 bg-gradient-to-r from-primary/10 to-accent/10 pointer-events-none" />
        </Button>

        <Button
          onClick={() => navigate("/journalists")}
          className="group relative px-6 py-3 bg-card/50 backdrop-blur-md border border-border/50 hover:border-primary/50 text-foreground hover:text-primary rounded-xl transition-all duration-300 hover:shadow-[0_0_20px_rgba(0,200,255,0.4)]"
        >
          <Users className="w-5 h-5 mr-2 inline-block transition-transform group-hover:scale-110" />
          <span className="font-semibold">All Journalists</span>
          
          {/* Glow effect on hover */}
          <div className="absolute inset-0 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 bg-gradient-to-r from-primary/10 to-accent/10 pointer-events-none" />
        </Button>
      </motion.div>

      {/* Interactive footer text - PERFECTLY CENTERED */}
      <div className="absolute bottom-8 left-0 right-0 w-full flex justify-center pointer-events-none">
        <motion.div
          onClick={scrollToNext}
          className="cursor-pointer select-none flex flex-col items-center gap-3 pointer-events-auto"
          animate={{ opacity: [0.6, 1, 0.6] }}
          transition={{ duration: 2, repeat: Infinity }}
        >
          <div className="relative inline-flex items-center justify-center">
            <span className="text-sm md:text-base tracking-widest font-semibold uppercase text-primary whitespace-nowrap">
              Dive into the Truth
            </span>
            <motion.div
              className="absolute left-1/2 top-1/2 w-24 h-24 -translate-x-1/2 -translate-y-1/2 rounded-full bg-primary/20 blur-2xl pointer-events-none"
              animate={{
                scale: [0.9, 1.4, 0.9],
                opacity: [0.2, 0.6, 0.2],
              }}
              transition={{
                duration: 3,
                repeat: Infinity,
                ease: "easeInOut",
              }}
            />
          </div>

          {/* Scrolling down icon */}
          <motion.div
            className="flex flex-col items-center justify-center"
            animate={{
              y: [0, 10, 0],
            }}
            transition={{
              duration: 1.5,
              repeat: Infinity,
              ease: "easeInOut",
            }}
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-6 w-6 text-primary drop-shadow-[0_0_8px_rgba(0,191,255,0.6)]"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M19 9l-7 7-7-7"
              />
            </svg>
          </motion.div>
        </motion.div>
      </div>
    </section>
  );
};

export default HeroSection;
