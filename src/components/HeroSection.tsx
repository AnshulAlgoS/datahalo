import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Users, Eye } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useMemo } from "react";
import ThemeToggle from "@/components/ThemeToggle";
import heroBg from "@/assets/hero-bg.jpeg";

/* Simple inline icons for light-mode background */

const BookIcon = (props: any) => (
  <svg viewBox="0 0 48 48" fill="none" {...props}>
    <rect
      x="8"
      y="10"
      width="14"
      height="22"
      rx="2.5"
      stroke="currentColor"
      strokeWidth="2"
      fill="white"
      fillOpacity="0.8"
    />
    <rect
      x="26"
      y="10"
      width="14"
      height="22"
      rx="2.5"
      stroke="currentColor"
      strokeWidth="2"
      fill="white"
      fillOpacity="0.8"
    />
    <path
      d="M11 15h8M11 19h8M11 23h8"
      stroke="currentColor"
      strokeWidth="1.6"
      strokeLinecap="round"
    />
    <path
      d="M29 15h8M29 19h8M29 23h8"
      stroke="currentColor"
      strokeWidth="1.6"
      strokeLinecap="round"
    />
  </svg>
);

const ArticleIcon = (props: any) => (
  <svg viewBox="0 0 40 40" fill="none" {...props}>
    <rect
      x="7"
      y="6"
      width="26"
      height="28"
      rx="4"
      stroke="currentColor"
      strokeWidth="1.8"
      fill="white"
      fillOpacity="0.9"
    />
    <rect x="11" y="11" width="8" height="6" rx="1.5" fill="currentColor" />
    <path
      d="M11 20h18M11 24h14M11 28h10"
      stroke="currentColor"
      strokeWidth="1.4"
      strokeLinecap="round"
      strokeOpacity="0.7"
    />
  </svg>
);

const LaptopIcon = (props: any) => (
  <svg viewBox="0 0 44 44" fill="none" {...props}>
    <rect
      x="10"
      y="11"
      width="24"
      height="16"
      rx="2"
      stroke="currentColor"
      strokeWidth="1.8"
      fill="white"
      fillOpacity="0.85"
    />
    <rect
      x="13"
      y="14"
      width="18"
      height="9"
      rx="1.5"
      fill="currentColor"
      fillOpacity="0.8"
    />
    <rect
      x="7"
      y="30"
      width="30"
      height="3"
      rx="1.5"
      fill="currentColor"
      fillOpacity="0.8"
    />
  </svg>
);

const MicIcon = (props: any) => (
  <svg viewBox="0 0 40 40" fill="none" {...props}>
    <rect
      x="15"
      y="9"
      width="10"
      height="16"
      rx="5"
      stroke="currentColor"
      strokeWidth="1.6"
      fill="white"
      fillOpacity="0.85"
    />
    <path
      d="M11 18v2a9 9 0 0 0 18 0v-2"
      stroke="currentColor"
      strokeWidth="1.6"
      strokeLinecap="round"
    />
    <path
      d="M20 28v4M16 32h8"
      stroke="currentColor"
      strokeWidth="1.6"
      strokeLinecap="round"
    />
  </svg>
);

const HeroSection = () => {
  const navigate = useNavigate();

  const scrollToNext = () => {
    document
      .getElementById("how-it-works")
      ?.scrollIntoView({ behavior: "smooth" });
  };

  // sparkles (dark mode only)
  const sparkleData = useMemo(
    () =>
      Array.from({ length: 12 }, () => ({
        leftOffset: (Math.random() - 0.5) * 100,
        xStart: (Math.random() - 0.5) * 50,
        xEnd: (Math.random() - 0.5) * 100,
        duration: 2 + Math.random() * 1,
        delay: Math.random() * 2,
      })),
    [],
  );

  // particles (dark mode only)
  const particleData = useMemo(
    () =>
      Array.from({ length: 20 }, () => ({
        left: 45 + Math.random() * 10,
        top: 20 + Math.random() * 60,
        blur: Math.random() * 1.5,
        duration: 3 + Math.random() * 2,
        delay: Math.random() * 2,
      })),
    [],
  );

  return (
    <section
      id="hero"
      className="relative min-h-screen flex flex-col items-center justify-center text-center overflow-hidden"
    >
      {/* ================================================================== */}
      {/* LIGHT MODE BACKGROUND – many side elements, center clean           */}
      {/* ================================================================== */}
      <div className="absolute inset-0 overflow-hidden dark:hidden pointer-events-none">
        {/* base gradients */}
        <div className="absolute inset-0 bg-gradient-to-br from-[#f6fbff] via-[#f2fbff] to-[#e9f5ff]" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_center,rgba(56,189,248,0.25),transparent_60%)]" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_bottom_center,rgba(56,189,248,0.18),transparent_60%)]" />

        {/* corner 3D blocks (4 big elements) */}
        <div
          className="absolute -left-24 -top-32 h-80 w-80 rounded-[2.5rem]"
          style={{
            background:
              "linear-gradient(135deg, rgba(178,233,255,0.7), rgba(216,244,255,0.18))",
            boxShadow:
              "0 35px 80px rgba(148,163,184,0.35), 0 0 0 1px rgba(148,163,184,0.25)",
            transform: "skewX(-8deg)",
          }}
        />
        <div
          className="absolute -right-32 bottom-[-80px] h-96 w-96 rounded-[2.5rem]"
          style={{
            background:
              "linear-gradient(155deg, rgba(165,232,255,0.9), rgba(213,246,255,0.22))",
            boxShadow:
              "0 -20px 60px rgba(56,189,248,0.6), 0 0 0 1px rgba(148,163,184,0.25)",
            transform: "skewX(-6deg)",
          }}
        />
        <div
          className="absolute -right-10 -top-20 h-52 w-52 rounded-[2rem]"
          style={{
            background:
              "linear-gradient(145deg, rgba(186,230,253,0.8), rgba(239,246,255,0.4))",
            boxShadow: "0 28px 60px rgba(148,163,184,0.38)",
          }}
        />
        <div
          className="absolute -left-16 bottom-[-60px] h-64 w-64 rounded-[2rem]"
          style={{
            background:
              "linear-gradient(160deg, rgba(191,219,254,0.8), rgba(239,246,255,0.5))",
            boxShadow: "0 -24px 60px rgba(148,163,184,0.35)",
          }}
        />

        {/* side circuitry panels + books (2 elements) */}
        <div className="absolute left-0 top-[40%] h-72 w-64">
          <div className="absolute left-6 top-10 h-40 w-32 rounded-[2rem] bg-cyan-100/75" />
          <div className="absolute inset-0 opacity-60">
            <div className="absolute inset-4 border-l border-t border-slate-200/80 rounded-xl" />
            <div className="absolute left-10 top-6 h-[70%] w-px bg-slate-200/80" />
            <div className="absolute left-[52%] top-0 h-[80%] w-px bg-slate-200/65" />
            <div className="absolute left-10 bottom-10 h-px w-28 bg-slate-200/65" />
            <div className="absolute left-[52%] bottom-6 h-px w-24 bg-slate-200/65" />
          </div>
          <BookIcon className="absolute left-7 top-8 h-16 w-16 text-cyan-500/85" />
        </div>

        <div className="absolute right-0 top-[18%] h-72 w-64">
          <div className="absolute right-6 top-10 h-40 w-32 rounded-[2rem] bg-cyan-100/70" />
          <div className="absolute inset-0 opacity-55">
            <div className="absolute inset-4 border-r border-t border-slate-200/80 rounded-xl" />
            <div className="absolute right-10 top-6 h-[70%] w-px bg-slate-200/80" />
            <div className="absolute right-[52%] top-0 h-[80%] w-px bg-slate-200/65" />
            <div className="absolute right-10 bottom-10 h-px w-28 bg-slate-200/65" />
            <div className="absolute right-[52%] bottom-6 h-px w-24 bg-slate-200/65" />
          </div>
          <BookIcon className="absolute right-7 top-8 h-16 w-16 text-cyan-500/85" />
        </div>

        {/* central halo – soft (just gradient, no shapes) */}
        <motion.div
          className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-[520px] h-[520px] rounded-full"
          style={{
            background:
              "radial-gradient(circle, rgba(56,189,248,0.32) 0%, rgba(56,189,248,0.14) 38%, transparent 70%)",
            filter: "blur(10px)",
          }}
          animate={{ opacity: [0.6, 0.85, 0.6], scale: [0.96, 1.04, 0.96] }}
          transition={{ duration: 7, repeat: Infinity, ease: "easeInOut" }}
        />

        {/* FLOATING GLASS CHIPS – kept away from text center */}
        {/* left column chips */}
        <motion.div
          className="absolute left-[6%] top-[26%] h-20 w-44 rounded-3xl border border-cyan-100/80 bg-white/80 backdrop-blur-xl shadow-[0_18px_50px_rgba(148,163,184,0.32)] flex items-center px-4 gap-3"
          animate={{ y: [-6, 6, -6], opacity: [0.85, 1, 0.85] }}
          transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
        >
          <ArticleIcon className="h-8 w-8 text-cyan-500/90" />
          <div className="text-left text-[11px] font-medium text-slate-700">
            Live news feeds
            <div className="text-[10px] text-cyan-500 font-semibold">
              Bias · Framing · Tone
            </div>
          </div>
        </motion.div>

        <motion.div
          className="absolute left-[4%] top-[52%] h-20 w-44 rounded-3xl border border-cyan-100/80 bg-white/75 backdrop-blur-xl shadow-[0_18px_50px_rgba(148,163,184,0.32)] flex items-center px-4 gap-3"
          animate={{ y: [5, -5, 5], opacity: [0.85, 1, 0.85] }}
          transition={{
            duration: 9,
            repeat: Infinity,
            ease: "easeInOut",
            delay: 0.4,
          }}
        >
          <BookIcon className="h-8 w-8 text-cyan-500/90" />
          <div className="text-left text-[11px] font-medium text-slate-700">
            Exam-ready notes
            <div className="text-[10px] text-cyan-500 font-semibold">
              UPSC · SSC · Media
            </div>
          </div>
        </motion.div>

        <motion.div
          className="absolute left-[9%] bottom-[10%] h-20 w-44 rounded-3xl border border-cyan-100/80 bg-white/80 backdrop-blur-xl shadow-[0_18px_50px_rgba(56,189,248,0.45)] flex items-center px-4 gap-3"
          animate={{ y: [-4, 4, -4], opacity: [0.9, 1, 0.9] }}
          transition={{
            duration: 10,
            repeat: Infinity,
            ease: "easeInOut",
            delay: 0.8,
          }}
        >
          <MicIcon className="h-8 w-8 text-cyan-500/90" />
          <div className="text-left text-[11px] font-medium text-slate-700">
            Journalist profiles
            <div className="text-[10px] text-cyan-500 font-semibold">
              Impact · Ethics · Reach
            </div>
          </div>
        </motion.div>

        {/* right column chips */}
        <motion.div
          className="absolute right-[7%] top-[24%] h-20 w-44 rounded-3xl border border-cyan-100/80 bg-white/80 backdrop-blur-xl shadow-[0_18px_50px_rgba(148,163,184,0.32)] flex items-center px-4 gap-3"
          animate={{ y: [4, -4, 4], opacity: [0.85, 1, 0.85] }}
          transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
        >
          <LaptopIcon className="h-8 w-8 text-cyan-500/90" />
          <div className="text-left text-[11px] font-medium text-slate-700">
            NVIDIA AI engine
            <div className="text-[10px] text-cyan-500 font-semibold">
              Real-time scoring
            </div>
          </div>
        </motion.div>

        <motion.div
          className="absolute right-[4%] top-[50%] h-20 w-44 rounded-3xl border border-cyan-100/80 bg-white/75 backdrop-blur-xl shadow-[0_18px_50px_rgba(148,163,184,0.32)] flex items-center px-4 gap-3"
          animate={{ y: [-5, 5, -5], opacity: [0.85, 1, 0.85] }}
          transition={{
            duration: 9,
            repeat: Infinity,
            ease: "easeInOut",
            delay: 0.5,
          }}
        >
          <BookIcon className="h-8 w-8 text-cyan-500/90" />
          <div className="text-left text-[11px] font-medium text-slate-700">
            Classroom mode
            <div className="text-[10px] text-cyan-500 font-semibold">
              Teachers & students
            </div>
          </div>
        </motion.div>

        <motion.div
          className="absolute right-[10%] bottom-[12%] h-20 w-44 rounded-3xl border border-cyan-100/80 bg-white/80 backdrop-blur-xl shadow-[0_18px_50px_rgba(56,189,248,0.45)] flex items-center px-4 gap-3"
          animate={{ y: [3, -3, 3], opacity: [0.9, 1, 0.9] }}
          transition={{
            duration: 10,
            repeat: Infinity,
            ease: "easeInOut",
            delay: 0.9,
          }}
        >
          <ArticleIcon className="h-8 w-8 text-cyan-500/90" />
          <div className="text-left text-[11px] font-medium text-slate-700">
            Case study builder
            <div className="text-[10px] text-cyan-500 font-semibold">
              Journalists · Topics
            </div>
          </div>
        </motion.div>

        {/* small floating mic icon – upper left (not behind text) */}
        <motion.div
          className="absolute left-[16%] top-[16%]"
          animate={{ y: [-4, 4, -4], opacity: [0.4, 0.7, 0.4] }}
          transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
        >
          <MicIcon className="h-9 w-9 text-cyan-400/70" />
        </motion.div>

        {/* tiny tech dots / nodes (~16 elements) around periphery */}
        {[
          { left: "18%", top: "72%" },
          { left: "22%", top: "24%" },
          { left: "26%", top: "80%" },
          { left: "30%", top: "18%" },
          { left: "12%", top: "55%" },
          { left: "10%", top: "32%" },
          { left: "78%", top: "22%" },
          { left: "82%", top: "68%" },
          { left: "86%", top: "32%" },
          { left: "74%", top: "78%" },
          { left: "70%", top: "18%" },
          { left: "88%", top: "50%" },
          { left: "50%", top: "10%" },
          { left: "52%", top: "86%" },
          { left: "40%", top: "90%" },
          { left: "60%", top: "90%" },
        ].map((pos, i) => (
          <motion.div
            key={i}
            className="absolute w-2.5 h-2.5 rounded-full bg-cyan-400/75 shadow-[0_0_10px_rgba(56,189,248,0.7)]"
            style={{ left: pos.left, top: pos.top }}
            animate={{ opacity: [0.3, 0.8, 0.3], scale: [0.8, 1.25, 0.8] }}
            transition={{
              duration: 4 + (i % 4),
              repeat: Infinity,
              ease: "easeInOut",
            }}
          />
        ))}
      </div>

      {/* ================================================================== */}
      {/* DARK MODE BACKGROUND – original cinematic hero (unchanged)        */}
      {/* ================================================================== */}
      <div className="absolute inset-0 hidden dark:block">
        <div
          className="absolute inset-0 bg-cover bg-center"
          style={{
            backgroundImage: `url(${heroBg})`,
            opacity: 0.35,
          }}
        />
        <div className="absolute inset-0 bg-gradient-to-b from-background/60 via-background/80 to-background/95" />

        <motion.div
          className="absolute bottom-0 left-1/2 w-[4px] h-full -translate-x-1/2 origin-bottom opacity-70"
          style={{
            background:
              "linear-gradient(to top, hsl(191 100% 60%) 0%, hsl(191 100% 55%) 20%, hsl(210 100% 60%) 50%, hsl(210 90% 55%) 80%, transparent 100%)",
            boxShadow:
              "0 0 30px hsl(191 100% 60%), 0 0 60px hsl(191 100% 50% / 0.6), 0 0 90px hsl(191 100% 50% / 0.3)",
            filter: "brightness(1.5)",
          }}
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

        <motion.div
          className="absolute bottom-0 left-1/2 w-[60px] h-full -translate-x-1/2 origin-bottom opacity-50"
          style={{
            background:
              "linear-gradient(to top, hsl(191 100% 60% / 0.4) 0%, hsl(191 100% 55% / 0.3) 20%, hsl(210 95% 60% / 0.2) 50%, hsl(210 90% 55% / 0.15) 70%, transparent 100%)",
            filter: "blur(30px)",
          }}
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

        <motion.div
          className="absolute bottom-0 left-1/2 w-[150px] h-full -translate-x-1/2 origin-bottom opacity-40"
          style={{
            background:
              "linear-gradient(to top, hsl(191 100% 60% / 0.3) 0%, hsl(191 95% 55% / 0.2) 25%, hsl(210 90% 60% / 0.15) 50%, transparent 75%)",
            filter: "blur(60px)",
          }}
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

        {[...Array(5)].map((_, i) => (
          <motion.div
            key={`pulse-${i}`}
            className="absolute bottom-0 left-1/2 w-[8px] h-[80px] -translate-x-1/2 rounded-full opacity-60"
            style={{
              background:
                "linear-gradient(to top, hsl(191 100% 70%) 0%, hsl(191 100% 60%) 50%, transparent 100%)",
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

        <motion.div
          className="absolute bottom-0 left-1/2 w-[300px] h-[150px] -translate-x-1/2 opacity-50"
          style={{
            background:
              "radial-gradient(ellipse at center, hsl(191 100% 65% / 0.6) 0%, hsl(191 100% 60% / 0.4) 30%, hsl(210 95% 60% / 0.2) 60%, transparent 100%)",
            filter: "blur(50px)",
          }}
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

        {sparkleData.map((data, i) => (
          <motion.div
            key={`sparkle-${i}`}
            className="absolute bottom-[20%] left-1/2 w-[3px] h-[3px] rounded-full opacity-70"
            style={{
              left: `calc(50% + ${data.leftOffset}px)`,
              background:
                i % 2 === 0 ? "hsl(191 100% 70%)" : "hsl(210 100% 70%)",
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

        <motion.div
          className="absolute inset-0 opacity-[0.3]"
          style={{
            background:
              "radial-gradient(circle at 50% 50%, hsl(191 100% 60% / 0.3) 0%, transparent 60%)",
            filter: "blur(80px)",
          }}
          animate={{
            opacity: [0.3, 0.45, 0.3],
            scale: [1, 1.05, 1],
          }}
          transition={{
            duration: 6,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />

        <motion.div
          className="absolute top-0 left-1/2 w-[300px] md:w-[500px] h-[600px] -translate-x-1/2 opacity-35"
          style={{
            background:
              "linear-gradient(180deg, hsl(191 100% 60% / 0.2) 0%, hsl(210 90% 60% / 0.15) 40%, transparent 100%)",
            filter: "blur(60px)",
          }}
          animate={{
            opacity: [0.25, 0.4, 0.25],
            scaleY: [1, 1.1, 1],
          }}
          transition={{
            duration: 4,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />

        <motion.div
          className="absolute top-0 left-1/2 w-[150px] md:w-[250px] h-[500px] -translate-x-1/2 opacity-35"
          style={{
            background:
              "linear-gradient(180deg, hsl(191 100% 55% / 0.25) 0%, hsl(210 95% 60% / 0.15) 50%, transparent 100%)",
            filter: "blur(40px)",
          }}
          animate={{ opacity: [0.25, 0.4, 0.25] }}
          transition={{
            duration: 3,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />

        <motion.div
          className="absolute top-0 left-1/2 w-[2px] h-[400px] -translate-x-1/2 opacity-40"
          style={{
            background:
              "linear-gradient(180deg, hsl(191 100% 60%) 0%, hsl(210 100% 60%) 50%, transparent 100%)",
            boxShadow:
              "0 0 20px hsl(191 100% 60% / 0.4), 0 0 40px hsl(191 100% 60% / 0.2)",
          }}
          animate={{ opacity: [0.3, 0.5, 0.3] }}
          transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
        />

        {[...Array(3)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute top-0 left-1/2 w-[400px] md:w-[600px] h-[400px] -translate-x-1/2 opacity-15"
            style={{
              background: `radial-gradient(ellipse at center, hsl(191 100% 55% / ${
                0.15 - i * 0.05
              }) 0%, transparent 70%)`,
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

        <motion.div
          className="absolute top-[50%] left-1/2 w-[500px] md:w-[800px] h-[200px] -translate-x-1/2 opacity-25"
          style={{
            background:
              "radial-gradient(ellipse at center, hsl(191 100% 60% / 0.3) 0%, hsl(210 90% 60% / 0.15) 40%, transparent 70%)",
            filter: "blur(80px)",
          }}
          animate={{
            opacity: [0.2, 0.35, 0.2],
            scaleX: [1, 1.1, 1],
          }}
          transition={{
            duration: 4,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />

        <motion.div
          className="absolute top-[60%] left-1/2 w-[600px] md:w-[1000px] h-[100px] -translate-x-1/2 opacity-30"
          style={{
            background:
              "radial-gradient(ellipse at center, hsl(191 100% 55% / 0.4) 0%, hsl(210 90% 60% / 0.2) 30%, transparent 70%)",
            filter: "blur(50px)",
          }}
          animate={{
            opacity: [0.25, 0.4, 0.25],
            scaleX: [1, 1.15, 1],
          }}
          transition={{
            duration: 3.5,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />

        {[...Array(8)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute top-0 left-1/2 w-[2px] h-[500px] -translate-x-1/2 origin-top opacity-10"
            style={{
              background:
                "linear-gradient(180deg, hsl(191 100% 60% / 0.3) 0%, transparent 100%)",
              transform: `translateX(-50%) rotate(${i * 45}deg)`,
              filter: "blur(2px)",
            }}
            animate={{ opacity: [0.05, 0.15, 0.05] }}
            transition={{
              duration: 3,
              repeat: Infinity,
              ease: "easeInOut",
              delay: i * 0.2,
            }}
          />
        ))}

        <motion.div
          className="absolute top-[40%] left-1/2 w-[100px] h-[100px] -translate-x-1/2 opacity-0"
          style={{
            background:
              "radial-gradient(circle, hsl(191 100% 60% / 0.4) 0%, transparent 70%)",
            filter: "blur(40px)",
          }}
          animate={{ opacity: [0, 0.25, 0], scale: [0.5, 2, 0.5] }}
          transition={{ duration: 4, repeat: Infinity, ease: "easeOut" }}
        />

        {particleData.map((data, i) => (
          <motion.div
            key={`particle-${i}`}
            className="absolute w-1 h-1 rounded-full opacity-50"
            style={{
              left: `${data.left}%`,
              top: `${data.top}%`,
              background:
                i % 2 === 0 ? "hsl(191 100% 60%)" : "hsl(210 90% 60%)",
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
      </div>

      {/* ================================================================== */}
      {/* SHARED CONTENT (text + button)                                    */}
      {/* ================================================================== */}
      <div className="relative z-10 px-6 max-w-5xl">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
        >
          <div className="font-orbitron mb-4 md:mb-6">
            {/* dark: original logo */}
            <span className="hidden dark:inline-block text-5xl md:text-7xl lg:text-8xl font-bold tracking-tight bg-gradient-to-r from-primary via-secondary to-primary bg-clip-text text-transparent animate-glow-pulse">
              DataHalo
            </span>

            {/* light: DATA (cyan) + HALO (grey) */}
            <span className="inline-block dark:hidden text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight">
              <span className="text-primary tracking-[0.25em]">DATA</span>
              <span className="ml-2 text-slate-500 tracking-[0.25em]">
                HALO
              </span>
            </span>
          </div>

          <h2 className="text-3xl md:text-5xl font-bold mb-4 text-foreground">
            AI-Powered Media Integrity
          </h2>

          <h3 className="text-xl md:text-2xl mb-6 md:mb-8 text-muted-foreground">
            for Journalists
          </h3>

          <p className="text-lg md:text-xl text-muted-foreground max-w-3xl mx-auto mb-10 md:mb-12 leading-relaxed">
            AI + NLP-backed verification of journalist authenticity.
            <br />
            <span className="text-primary font-semibold">
              Rebuilding Trust in Media — One Article at a Time.
            </span>
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Button
              size="lg"
              className="relative px-8 py-6 text-lg font-semibold bg-primary hover:bg-primary/90 text-primary-foreground rounded-full overflow-hidden group shadow-[0_18px_40px_rgba(0,191,255,0.6)]"
            >
              <span className="relative z-10">View Demo</span>
              <div className="absolute inset-0 bg-gradient-to-r from-primary to-accent opacity-0 group-hover:opacity-100 transition-opacity" />
            </Button>
          </div>
        </motion.div>
      </div>

      {/* TOP RIGHT BUTTONS */}
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
          <div className="absolute inset-0 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 bg-gradient-to-r from-primary/10 to-accent/10 pointer-events-none" />
        </Button>

        <Button
          onClick={() => navigate("/journalists")}
          className="group relative px-6 py-3 bg-card/50 backdrop-blur-md border border-border/50 hover:border-primary/50 text-foreground hover:text-primary rounded-xl transition-all duration-300 hover:shadow-[0_0_20px_rgba(0,200,255,0.4)]"
        >
          <Users className="w-5 h-5 mr-2 inline-block transition-transform group-hover:scale-110" />
          <span className="font-semibold">All Journalists</span>
          <div className="absolute inset-0 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 bg-gradient-to-r from-primary/10 to-accent/10 pointer-events-none" />
        </Button>
      </motion.div>

      {/* FOOTER SCROLL CTA */}
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

          <motion.div
            className="flex flex-col items-center justify-center"
            animate={{ y: [0, 10, 0] }}
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
