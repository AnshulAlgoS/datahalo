import { Home, Zap, Grid3x3, BarChart3, Globe, DollarSign, Mail } from "lucide-react";
import { motion } from "framer-motion";

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
  const scrollToSection = (id: string) => {
    const element = document.getElementById(id);
    element?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <motion.nav
      initial={{ x: -100, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ duration: 0.6 }}
      className="fixed left-6 top-1/2 -translate-y-1/2 z-40 hidden lg:flex flex-col gap-6"
    >
      {navItems.map((item, index) => (
        <motion.button
          key={item.id}
          initial={{ x: -50, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.4, delay: index * 0.1 }}
          onClick={() => scrollToSection(item.id)}
          className="group relative flex items-center justify-center w-12 h-12 rounded-xl bg-card/50 backdrop-blur-md border border-border/50 hover:border-primary/50 hover:bg-card transition-all duration-300"
          style={{ boxShadow: "0 4px 12px hsl(var(--navy-dark) / 0.3)" }}
        >
          <item.icon className="w-5 h-5 text-muted-foreground group-hover:text-primary transition-colors" />
          
          {/* Tooltip */}
          <div className="absolute left-16 px-3 py-2 bg-card border border-primary/30 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap">
            <p className="text-sm font-medium text-foreground">{item.label}</p>
          </div>

          {/* Glow effect on hover */}
          <div className="absolute inset-0 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity"
            style={{ boxShadow: "0 0 20px hsl(var(--glow-cyan) / 0.4)" }} />
        </motion.button>
      ))}
    </motion.nav>
  );
};

export default SideNav;