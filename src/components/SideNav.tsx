import { Home, Zap, Grid3x3, BarChart3, Globe, DollarSign, Mail } from "lucide-react";
import { motion } from "framer-motion";
import { useState } from "react";

const navItems = [
  { id: "hero", icon: Home, label: "Home" },
  { id: "how-it-works", icon: Zap, label: "How It Works" },
  { id: "features", icon: Grid3x3, label: "Features" },
  { id: "dashboard", icon: BarChart3, label: "Dashboard" },
  { id: "impact", icon: Globe, label: "Impact" },
  { id: "revenue", icon: DollarSign, label: "Revenue" },
  { id: "contact", icon: Mail, label: "Contact" },
];

const SideNav = () => {
  const [active, setActive] = useState<string>("hero");

  const scrollToSection = (id: string) => {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: "smooth" });
      setActive(id);
    }
  };

  return (
    <>
      {/* 🖥️ Desktop Sidebar */}
      <motion.nav
        initial={{ x: -100, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        transition={{ duration: 0.6 }}
        className="fixed inset-y-0 left-6 z-40 hidden lg:flex flex-col justify-center gap-6"
      >
        {navItems.map((item, index) => (
          <motion.button
            key={item.id}
            initial={{ x: -50, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ duration: 0.4, delay: index * 0.1 }}
            onClick={() => scrollToSection(item.id)}
            className={`group relative flex items-center justify-center w-12 h-12 rounded-xl bg-card/50 backdrop-blur-md border ${
              active === item.id
                ? "border-primary shadow-[0_0_12px_rgba(0,200,255,0.4)]"
                : "border-border/50"
            } hover:border-primary/50 hover:bg-card transition-all duration-300`}
            style={{ boxShadow: "0 4px 12px hsl(var(--navy-dark) / 0.3)" }}
          >
            <item.icon
              className={`w-5 h-5 transition-colors ${
                active === item.id
                  ? "text-primary"
                  : "text-muted-foreground group-hover:text-primary"
              }`}
            />

            {/* Tooltip */}
            <div className="absolute left-16 px-3 py-2 bg-card border border-primary/30 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap">
              <p className="text-sm font-medium text-foreground">{item.label}</p>
            </div>

            {/* Glow effect */}
            <div
              className="absolute inset-0 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity"
              style={{ boxShadow: "0 0 20px hsl(var(--glow-cyan) / 0.4)" }}
            />
          </motion.button>
        ))}
      </motion.nav>

      {/* 📱 Mobile Bottom Nav */}
      <motion.nav
        initial={{ y: 100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6 }}
        className="fixed bottom-4 left-1/2 -translate-x-1/2 z-40 flex lg:hidden items-center justify-around w-[90%] max-w-md bg-card/60 backdrop-blur-md border border-border/50 rounded-2xl px-3 py-2"
      >
        {navItems.map((item, index) => (
          <motion.button
            key={item.id}
            initial={{ y: 50, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.4, delay: index * 0.05 }}
            onClick={() => scrollToSection(item.id)}
            className={`flex flex-col items-center justify-center p-2 transition-all ${
              active === item.id ? "text-primary" : "text-muted-foreground hover:text-primary"
            }`}
          >
            <item.icon className="w-5 h-5" />
          </motion.button>
        ))}
      </motion.nav>
    </>
  );
};

export default SideNav;
