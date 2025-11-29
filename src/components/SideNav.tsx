import { Home, Zap, Grid3x3, Search, Globe, Newspaper, Mail, User, LogOut, LayoutDashboard } from "lucide-react";
import { motion } from "framer-motion";
import { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { toast } from "sonner";

const navItems = [
  { id: "hero", icon: Home, label: "Home" },
  { id: "how-it-works", icon: Zap, label: "How It Works" },
  { id: "features", icon: Grid3x3, label: "Features" },
  { id: "analyzer", icon: Search, label: "Analyzer" },
  { id: "impact", icon: Globe, label: "Impact" },
  { id: "news", icon: Newspaper, label: "News" }, 
  { id: "contact", icon: Mail, label: "Contact" },
];

const SideNav = () => {
  const [active, setActive] = useState<string>("hero");
  const navigate = useNavigate();
  const { currentUser, userProfile, logout } = useAuth();

  const handleLogout = async () => {
    try {
      await logout();
      toast.success("Logged out successfully");
      navigate("/");
    } catch (error) {
      toast.error("Failed to log out");
    }
  };

  const scrollToSection = (id: string) => {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: "smooth" });
      setActive(id);
    }
  };

  // Track scroll position for active state
  useEffect(() => {
    const handleScroll = () => {
      let currentSection = active;
      for (const item of navItems) {
        const section = document.getElementById(item.id);
        if (section) {
          const rect = section.getBoundingClientRect();
          if (
            rect.top <= window.innerHeight / 2 &&
            rect.bottom >= window.innerHeight / 2
          ) {
            currentSection = item.id;
            break;
          }
        }
      }
      setActive(currentSection);
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, [active]);

  return (
    <>
      {/* Desktop Sidebar with Auth */}
      <motion.nav
        initial={{ x: -100, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        transition={{ duration: 0.6 }}
        className="fixed inset-y-0 left-6 z-40 hidden lg:flex flex-col justify-between py-6"
      >
        {/* Navigation Items */}
        <div className="flex flex-col justify-center gap-6 flex-1">
          {navItems.map((item) => (
            <motion.button
              key={item.id}
              onClick={() => scrollToSection(item.id)}
              className={`group relative flex items-center justify-center w-12 h-12 rounded-xl bg-card/50 backdrop-blur-md border transition-all duration-300 ${
                active === item.id
                  ? "border-primary shadow-[0_0_20px_rgba(0,200,255,0.6)]"
                  : "border-border/50 hover:border-primary/50 hover:bg-card"
              }`}
            >
              <item.icon
                className={`w-5 h-5 transition-all ${
                  active === item.id
                    ? "text-primary drop-shadow-[0_0_12px_rgba(0,200,255,0.6)]"
                    : "text-muted-foreground group-hover:text-primary"
                }`}
              />
              <div className="absolute left-16 px-3 py-2 bg-card border border-primary/30 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap">
                <p className="text-sm font-medium text-foreground">{item.label}</p>
              </div>
            </motion.button>
          ))}
        </div>

        {/* Auth Section at Bottom */}
        <div className="flex flex-col gap-3">
          {currentUser && userProfile ? (
            <>
              {/* Dashboard Button */}
              <motion.button
                onClick={() => navigate("/dashboard")}
                className="group relative flex items-center justify-center w-12 h-12 rounded-xl bg-card/50 backdrop-blur-md border border-border/50 hover:border-primary/50 hover:bg-card transition-all duration-300"
              >
                <LayoutDashboard className="w-5 h-5 text-muted-foreground group-hover:text-primary transition-all" />
                <div className="absolute left-16 px-3 py-2 bg-card border border-primary/30 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap">
                  <p className="text-sm font-medium text-foreground">Dashboard</p>
                </div>
              </motion.button>

              {/* User Profile */}
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <motion.button className="group relative flex items-center justify-center w-12 h-12 rounded-xl bg-card/50 backdrop-blur-md border border-border/50 hover:border-primary/50 hover:bg-card transition-all duration-300">
                    <Avatar className="h-8 w-8">
                      <AvatarImage src={userProfile.photoURL} alt={userProfile.displayName} />
                      <AvatarFallback className="bg-gradient-to-r from-blue-600 to-purple-600 text-white text-xs">
                        {userProfile.displayName.charAt(0)}
                      </AvatarFallback>
                    </Avatar>
                    <div className="absolute left-16 px-3 py-2 bg-card border border-primary/30 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap">
                      <p className="text-sm font-medium text-foreground">Profile</p>
                    </div>
                  </motion.button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="start" side="right" className="w-56 ml-2">
                  <DropdownMenuLabel>
                    <div className="flex flex-col space-y-1">
                      <p className="text-sm font-medium">{userProfile.displayName}</p>
                      <p className="text-xs text-muted-foreground">{userProfile.email}</p>
                      <p className="text-xs text-muted-foreground capitalize">
                        {userProfile.role}
                      </p>
                    </div>
                  </DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={() => navigate("/dashboard")}>
                    <LayoutDashboard className="mr-2 h-4 w-4" />
                    Dashboard
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={handleLogout} className="text-red-600">
                    <LogOut className="mr-2 h-4 w-4" />
                    Log out
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </>
          ) : (
            <>
              {/* Login Button */}
              <motion.button
                onClick={() => navigate("/login")}
                className="group relative flex items-center justify-center w-12 h-12 rounded-xl bg-card/50 backdrop-blur-md border border-border/50 hover:border-primary/50 hover:bg-card transition-all duration-300"
              >
                <User className="w-5 h-5 text-muted-foreground group-hover:text-primary transition-all" />
                <div className="absolute left-16 px-3 py-2 bg-card border border-primary/30 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap">
                  <p className="text-sm font-medium text-foreground">Sign In</p>
                </div>
              </motion.button>
            </>
          )}
        </div>
      </motion.nav>

      {/* Mobile Bottom Nav with Auth */}
      <motion.nav
        initial={{ y: 100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6 }}
        className="fixed bottom-4 left-1/2 -translate-x-1/2 z-40 flex lg:hidden items-center justify-around w-[95%] max-w-md bg-card/60 backdrop-blur-md border border-border/50 rounded-2xl px-2 py-2"
      >
        {navItems.map((item) => (
          <motion.button
            key={item.id}
            onClick={() => scrollToSection(item.id)}
            className={`flex flex-col items-center justify-center p-2 transition-all ${
              active === item.id
                ? "text-primary"
                : "text-muted-foreground hover:text-primary"
            }`}
          >
            <item.icon
              className={`w-5 h-5 transition-all ${
                active === item.id
                  ? "text-primary drop-shadow-[0_0_8px_rgba(0,200,255,0.6)]"
                  : ""
              }`}
            />
          </motion.button>
        ))}

        {/* Auth Section for Mobile */}
        <div className="border-l border-border/50 pl-2 ml-2">
          {currentUser && userProfile ? (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <motion.button className="flex items-center justify-center p-2">
                  <Avatar className="h-7 w-7">
                    <AvatarImage src={userProfile.photoURL} alt={userProfile.displayName} />
                    <AvatarFallback className="bg-gradient-to-r from-blue-600 to-purple-600 text-white text-xs">
                      {userProfile.displayName.charAt(0)}
                    </AvatarFallback>
                  </Avatar>
                </motion.button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" side="top" className="w-56 mb-2">
                <DropdownMenuLabel>
                  <div className="flex flex-col space-y-1">
                    <p className="text-sm font-medium">{userProfile.displayName}</p>
                    <p className="text-xs text-muted-foreground">{userProfile.email}</p>
                    <p className="text-xs text-muted-foreground capitalize">
                      {userProfile.role}
                    </p>
                  </div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={() => navigate("/dashboard")}>
                  <LayoutDashboard className="mr-2 h-4 w-4" />
                  Dashboard
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={handleLogout} className="text-red-600">
                  <LogOut className="mr-2 h-4 w-4" />
                  Log out
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          ) : (
            <motion.button
              onClick={() => navigate("/login")}
              className="flex items-center justify-center p-2 text-muted-foreground hover:text-primary transition-all"
            >
              <User className="w-5 h-5" />
            </motion.button>
          )}
        </div>
      </motion.nav>
    </>
  );
};

export default SideNav;