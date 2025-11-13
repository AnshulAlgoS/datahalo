import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import heroBg from "@/assets/hero-bg.jpeg";

const HeroSection = () => {
  const scrollToNext = () => {
    document.getElementById("how-it-works")?.scrollIntoView({ behavior: "smooth" });
  };

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
          filter: "brightness(0.45)",
        }}
      />

      {/* Gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-b from-background/80 via-background/60 to-background/90" />

      {/* ⚡ ENHANCED Lightning flash pulse - More dramatic */}
      <motion.div
        className="absolute inset-0 bg-gradient-to-t from-[#00bfff15] via-[#00bfff35] to-transparent pointer-events-none"
        animate={{
          opacity: [0, 0.3, 0, 0.6, 0, 0.9, 0],
          filter: [
            "brightness(1)",
            "brightness(1.4)",
            "brightness(1)",
            "brightness(1.6)",
            "brightness(1)",
            "brightness(2)",
            "brightness(1)",
          ],
        }}
        transition={{
          duration: 4,
          repeat: Infinity,
          repeatType: "mirror",
          ease: "easeInOut",
        }}
      />

      {/* ⚡ Intense bottom glow base for sword */}
      <motion.div
        className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[120px] h-[120px] bg-[#00bfff] rounded-full blur-[40px]"
        animate={{
          opacity: [0.6, 1, 0.6],
          scale: [0.9, 1.2, 0.9],
          boxShadow: [
            "0 0 40px #00bfff",
            "0 0 80px #00bfff",
            "0 0 40px #00bfff",
          ],
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />

      {/* 🌌 CORE Lightning beam - Brighter and sharper */}
      <motion.div
        className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[6px] h-full bg-gradient-to-t from-[#ffffff] via-[#00bfff] to-transparent"
        animate={{
          opacity: [0.7, 1, 0.7],
          scaleY: [1, 1.1, 1],
          filter: [
            "drop-shadow(0 0 8px #00bfff)",
            "drop-shadow(0 0 16px #00bfff)",
            "drop-shadow(0 0 8px #00bfff)",
          ],
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />

      {/* Lightning sword outer glow - Wide spread */}
      <motion.div
        className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[16px] h-full bg-gradient-to-t from-[#00bfff95] via-[#00bfff50] to-transparent blur-[12px]"
        animate={{
          opacity: [0.5, 0.9, 0.5],
          scaleX: [1, 1.2, 1],
        }}
        transition={{
          duration: 2.5,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />

      {/* Additional intense glow layer */}
      <motion.div
        className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[24px] h-full bg-gradient-to-t from-[#00bfff80] via-[#00bfff30] to-transparent blur-[20px]"
        animate={{
          opacity: [0.4, 0.8, 0.4],
        }}
        transition={{
          duration: 3,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />

      {/* ⚡ RAPID Moving energy - Primary strike */}
      <motion.div
        className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[16px] h-[250px] bg-gradient-to-t from-[#ffffff] via-[#00bfff] to-transparent blur-[6px] rounded-full"
        animate={{
          y: ["0%", "-400%"],
          opacity: [1, 0.9, 0.6, 0.2, 0],
          scaleX: [1.2, 1, 0.8, 0.5, 0.3],
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
          ease: "easeOut",
        }}
      />

      {/* ⚡ Secondary strike - Delayed for effect */}
      <motion.div
        className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[14px] h-[220px] bg-gradient-to-t from-[#ffffff] via-[#00d4ff] to-transparent blur-[5px]"
        animate={{
          y: ["0%", "-420%"],
          opacity: [0.95, 0.7, 0.4, 0],
          scaleX: [1.1, 0.9, 0.6, 0.4],
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
          ease: "easeOut",
          delay: 0.4,
        }}
      />

      {/* ⚡ Tertiary strike - More variation */}
      <motion.div
        className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[12px] h-[200px] bg-gradient-to-t from-[#00e5ff] via-[#00bfff70] to-transparent blur-[7px]"
        animate={{
          y: ["0%", "-380%"],
          opacity: [0.9, 0.6, 0.3, 0],
          scaleX: [1, 0.7, 0.5, 0.3],
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
          ease: "easeOut",
          delay: 0.8,
        }}
      />

      {/* Electric sparks effect */}
      <motion.div
        className="absolute bottom-20 left-1/2 -translate-x-1/2 w-[30px] h-[30px] bg-[#00bfff] rounded-full blur-[8px]"
        animate={{
          y: [0, -100, -200, -300],
          x: [0, 10, -10, 0],
          opacity: [0.8, 0.6, 0.3, 0],
          scale: [1, 0.8, 0.5, 0.2],
        }}
        transition={{
          duration: 1.8,
          repeat: Infinity,
          ease: "easeOut",
        }}
      />

      {/* Electric sparks effect - opposite side */}
      <motion.div
        className="absolute bottom-20 left-1/2 -translate-x-1/2 w-[25px] h-[25px] bg-[#00d4ff] rounded-full blur-[6px]"
        animate={{
          y: [0, -120, -240, -360],
          x: [0, -15, 15, 0],
          opacity: [0.7, 0.5, 0.2, 0],
          scale: [0.9, 0.7, 0.4, 0.1],
        }}
        transition={{
          duration: 1.8,
          repeat: Infinity,
          ease: "easeOut",
          delay: 0.5,
        }}
      />

      {/* ⚡ Lightning flicker effect */}
      <motion.div
        className="absolute inset-0 bg-gradient-to-b from-transparent via-[#00bfff20] to-transparent pointer-events-none"
        animate={{
          opacity: [0, 0.8, 0, 0.6, 0, 1, 0],
        }}
        transition={{
          duration: 0.3,
          repeat: Infinity,
          repeatDelay: 3,
          ease: "linear",
        }}
      />

      {/* Enhanced center glow */}
      <motion.div
        animate={{ 
          scale: [1, 1.2, 1], 
          opacity: [0.4, 0.7, 0.4],
        }}
        transition={{ duration: 3, repeat: Infinity }}
        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[32rem] h-[32rem] bg-primary/30 rounded-full blur-[100px]"
      />

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
