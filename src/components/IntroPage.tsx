import { useEffect, useState } from "react";
import { motion } from "framer-motion";

interface IntroPageProps {
  onComplete: () => void;
}

const IntroPage = ({ onComplete }: IntroPageProps) => {
  const [show, setShow] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setShow(false);
      setTimeout(onComplete, 800);
    }, 3500);

    return () => clearTimeout(timer);
  }, [onComplete]);

  return (
    <motion.div
      initial={{ opacity: 1 }}
      animate={{ opacity: show ? 1 : 0 }}
      transition={{ duration: 0.8 }}
      className="fixed inset-0 z-50 flex items-center justify-center bg-background overflow-hidden"
    >
      {/* Glow effect background */}
      <div className="absolute inset-0 bg-gradient-radial from-primary/20 via-transparent to-transparent" />
      
      {/* Vertical light beam */}
      <motion.div
        initial={{ scaleY: 0, opacity: 0 }}
        animate={{ scaleY: 1, opacity: 1 }}
        transition={{ duration: 1.5, ease: "easeOut" }}
        className="absolute inset-x-0 top-0 h-full w-1 mx-auto bg-gradient-to-b from-transparent via-primary to-transparent opacity-60"
        style={{ filter: "blur(2px)" }}
      />

      {/* Main logo text */}
      <motion.div
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 1, delay: 0.5 }}
        className="relative z-10"
      >
        <h1 className="font-orbitron text-6xl md:text-8xl font-bold tracking-[0.3em] text-foreground uppercase">
          <span className="inline-block animate-glow-pulse" style={{ textShadow: "0 0 30px hsl(var(--glow-cyan)), 0 0 60px hsl(var(--glow-cyan) / 0.5)" }}>
            DataHalo
          </span>
        </h1>
        
        {/* Center glow point */}
        <motion.div
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 1, delay: 1 }}
          className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-4 h-4 bg-primary rounded-full"
          style={{ boxShadow: "0 0 60px 20px hsl(var(--glow-cyan))" }}
        />
      </motion.div>

      {/* Animated particles */}
      {[...Array(20)].map((_, i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0, scale: 0 }}
          animate={{ 
            opacity: [0, 1, 0], 
            scale: [0, 1, 0],
            x: [0, (Math.random() - 0.5) * 400],
            y: [0, (Math.random() - 0.5) * 400],
          }}
          transition={{ 
            duration: 2, 
            delay: 1 + (i * 0.1),
            ease: "easeOut"
          }}
          className="absolute top-1/2 left-1/2 w-1 h-1 bg-primary rounded-full"
          style={{ boxShadow: "0 0 10px hsl(var(--glow-cyan))" }}
        />
      ))}
    </motion.div>
  );
};

export default IntroPage;