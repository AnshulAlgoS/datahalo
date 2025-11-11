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
      {/* Massive central radial glow */}
      <motion.div
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: 3, opacity: 1 }}
        transition={{ duration: 1.5, ease: "easeOut" }}
        className="absolute inset-0 bg-gradient-radial from-primary/70 via-primary/30 to-transparent"
      />

      {/* Cinematic vertical energy beam */}
      <motion.div
        initial={{ height: 0, opacity: 0 }}
        animate={{ height: "200%", opacity: 0.6 }}
        transition={{ duration: 1.2, ease: "easeOut" }}
        className="absolute left-1/2 w-2 bg-gradient-to-t from-primary/80 via-primary/40 to-transparent"
        style={{
          transform: "translateX(-50%)",
          filter: "blur(12px)",
        }}
      />

      {/* Exploding layered rings */}
      {[250, 400, 600].map((size, idx) => (
        <motion.div
          key={idx}
          initial={{ scale: 0, opacity: 0.5 }}
          animate={{ scale: 1, opacity: 0 }}
          transition={{
            duration: 2 + idx * 0.5,
            repeat: Infinity,
            repeatType: "loop",
            ease: "easeOut",
            delay: idx * 0.1,
          }}
          className="absolute top-1/2 left-1/2 rounded-full border border-primary"
          style={{
            width: size,
            height: size,
            marginLeft: -size / 2,
            marginTop: -size / 2,
            filter: "blur(40px)",
          }}
        />
      ))}

      {/* Main logo */}
      <motion.div
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 1, delay: 0.5 }}
        className="relative z-10 flex flex-col items-center"
      >
        <h1
          className="font-orbitron text-6xl md:text-8xl font-bold tracking-[0.3em] text-foreground uppercase"
          style={{
            textShadow:
              "0 0 80px hsl(var(--glow-cyan)), 0 0 200px hsl(var(--glow-cyan)/0.7)",
          }}
        >
          DataHalo
        </h1>
      </motion.div>

      {/* Ultra-spread particles */}
      {[...Array(80)].map((_, i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0, scale: 0 }}
          animate={{
            opacity: [0, 1, 0],
            scale: [0, 1, 0],
            x: [0, (Math.random() - 0.5) * 1800],
            y: [0, (Math.random() - 0.5) * 1200],
          }}
          transition={{
            duration: 2 + Math.random() * 2,
            delay: 0.3 + i * 0.02,
            ease: "easeOut",
          }}
          className="absolute top-1/2 left-1/2 w-2 h-2 bg-primary rounded-full"
          style={{ boxShadow: "0 0 35px hsl(var(--glow-cyan))" }}
        />
      ))}
    </motion.div>
  );
};

export default IntroPage;
