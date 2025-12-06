import { motion } from "framer-motion";
import { Mail, Phone, Send, Github, Twitter, Linkedin, ExternalLink, Shield, Eye, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";

const contactMethods = [
  {
    icon: Phone,
    title: "Schedule a Call",
    description: "Book a discovery call to discuss your needs",
    cta: "Book Now",
    href: "#"
  },
  {
    icon: Mail,
    title: "Send an Enquiry",
    description: "Prefer to share details in writing?",
    cta: "Contact Us",
    href: "mailto:contact@datahalo.com"
  },
  {
    icon: Send,
    title: "Get Demo Access",
    description: "Try our platform with a free demo",
    cta: "Request Demo",
    href: "#"
  },
];

const footerLinks = {
  product: [
    { name: "Journalist Analyzer", href: "/analyze" },
    { name: "Narrative Tracker", href: "/narrative-analyzer" },
    { name: "Journalists Gallery", href: "/journalists" },
    { name: "News Feed", href: "/news" },
  ],
  resources: [
    { name: "API Documentation", href: "#" },
    { name: "Halo Score Guide", href: "#" },
    { name: "Research Papers", href: "#" },
    { name: "Media Literacy Hub", href: "#" },
  ],
  company: [
    { name: "About Us", href: "#" },
    { name: "Our Mission", href: "#" },
    { name: "Claim Your Profile", href: "#" },
    { name: "For Researchers", href: "#" },
  ],
  legal: [
    { name: "Privacy Policy", href: "#" },
    { name: "Terms of Service", href: "#" },
    { name: "Data Usage", href: "#" },
    { name: "Contact", href: "#" },
  ],
};

const socialLinks = [
  { icon: Github, href: "https://github.com/datahalo", label: "GitHub" },
  { icon: Twitter, href: "https://twitter.com/datahalo", label: "Twitter" },
  { icon: Linkedin, href: "https://linkedin.com/company/datahalo", label: "LinkedIn" },
];

const Contact = () => {
  return (
    <section id="contact" className="relative min-h-screen flex items-center py-24 px-6 overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0">
        <div className="absolute inset-0 bg-gradient-to-b from-background via-primary/5 to-background" />
        {/* Animated gradient orbs */}
        <motion.div
          animate={{ 
            scale: [1, 1.2, 1],
            opacity: [0.3, 0.5, 0.3],
          }}
          transition={{ duration: 8, repeat: Infinity }}
          className="absolute top-20 right-20 w-96 h-96 bg-primary/20 rounded-full blur-[120px]"
        />
        <motion.div
          animate={{ 
            scale: [1.2, 1, 1.2],
            opacity: [0.2, 0.4, 0.2],
          }}
          transition={{ duration: 10, repeat: Infinity }}
          className="absolute bottom-20 left-20 w-96 h-96 bg-accent/20 rounded-full blur-[120px]"
        />
      </div>

      <div className="relative z-10 max-w-7xl mx-auto w-full">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="font-orbitron text-4xl md:text-6xl font-bold mb-6">
            Get in <span className="text-primary">Touch</span>
          </h2>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            Ready to restore trust in journalism? Let's connect and discuss how DataHalo can help.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-8 mb-20">
          {contactMethods.map((method, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.2 }}
              viewport={{ once: true }}
              className="text-center"
            >
              <div className="relative p-8 rounded-2xl bg-card/40 backdrop-blur-md border border-border/50 hover:border-primary/50 transition-all duration-300 group">
                {/* Glow effect */}
                <div
                  className="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"
                  style={{
                    boxShadow: "0 0 40px hsl(var(--glow-cyan) / 0.3)",
                  }}
                />

                {/* Icon */}
                <div className="mb-6 inline-flex p-6 rounded-2xl bg-primary/10 border border-primary/30 group-hover:scale-110 transition-transform duration-300">
                  <method.icon className="w-12 h-12 text-primary" />
                </div>

                {/* Content */}
                <h3 className="text-2xl font-bold mb-3 text-foreground">{method.title}</h3>
                <p className="text-muted-foreground mb-6">{method.description}</p>

                {/* CTA Button */}
                <Button 
                  className="w-full bg-primary hover:bg-primary/90 text-primary-foreground rounded-xl group-hover:scale-105 transition-transform"
                  size="lg"
                  asChild
                >
                  <a href={method.href}>
                    {method.cta}
                    <ExternalLink className="w-4 h-4 ml-2" />
                  </a>
                </Button>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Enhanced Footer */}
        <motion.footer
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          viewport={{ once: true }}
          className="pt-16 border-t border-border/50"
        >
          {/* Main Footer Content */}
          <div className="grid md:grid-cols-2 lg:grid-cols-6 gap-12 mb-12">
            {/* Brand Section */}
            <div className="lg:col-span-2">
              <div className="flex items-center gap-2 mb-4">
                <div className="p-2 bg-primary/10 border border-primary/30 rounded-lg">
                  <Eye className="w-6 h-6 text-primary" />
                </div>
                <h3 className="font-orbitron text-3xl font-bold">
                  <span className="text-primary">DataHalo</span>
                </h3>
              </div>
              
              {/* Tagline */}
              <p className="text-lg font-semibold text-foreground mb-2 italic">
                "The Story Behind the Storyteller"
              </p>
              
              <p className="text-sm text-muted-foreground mb-6 leading-relaxed">
                Empowering media transparency through AI-driven journalist analysis and narrative tracking. 
                Built for everyone — from general readers to academic researchers.
              </p>

              {/* Key Features Badges */}
              <div className="flex flex-wrap gap-2 mb-6">
                <div className="flex items-center gap-1 px-3 py-1 rounded-full bg-primary/10 border border-primary/30 text-xs">
                  <Shield className="w-3 h-3" />
                  <span>Halo Score™</span>
                </div>
                <div className="flex items-center gap-1 px-3 py-1 rounded-full bg-primary/10 border border-primary/30 text-xs">
                  <Sparkles className="w-3 h-3" />
                  <span>AI-Powered</span>
                </div>
                <div className="flex items-center gap-1 px-3 py-1 rounded-full bg-primary/10 border border-primary/30 text-xs">
                  <Eye className="w-3 h-3" />
                  <span>Open Source</span>
                </div>
              </div>

              {/* Social Links */}
              <div className="flex gap-4">
                {socialLinks.map((social, idx) => (
                  <a
                    key={idx}
                    href={social.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="p-2 rounded-lg bg-card/50 border border-border/50 hover:border-primary/50 hover:bg-primary/10 transition-all group"
                    aria-label={social.label}
                  >
                    <social.icon className="w-5 h-5 text-muted-foreground group-hover:text-primary transition-colors" />
                  </a>
                ))}
              </div>
            </div>

            {/* Product Links */}
            <div>
              <h4 className="font-semibold text-foreground mb-4">Product</h4>
              <ul className="space-y-3">
                {footerLinks.product.map((link, idx) => (
                  <li key={idx}>
                    <a
                      href={link.href}
                      className="text-sm text-muted-foreground hover:text-primary transition-colors flex items-center gap-1 group"
                    >
                      <span className="group-hover:translate-x-1 transition-transform">{link.name}</span>
                    </a>
                  </li>
                ))}
              </ul>
            </div>

            {/* Resources Links */}
            <div>
              <h4 className="font-semibold text-foreground mb-4">Resources</h4>
              <ul className="space-y-3">
                {footerLinks.resources.map((link, idx) => (
                  <li key={idx}>
                    <a
                      href={link.href}
                      className="text-sm text-muted-foreground hover:text-primary transition-colors flex items-center gap-1 group"
                    >
                      <span className="group-hover:translate-x-1 transition-transform">{link.name}</span>
                    </a>
                  </li>
                ))}
              </ul>
            </div>

            {/* Company Links */}
            <div>
              <h4 className="font-semibold text-foreground mb-4">Company</h4>
              <ul className="space-y-3">
                {footerLinks.company.map((link, idx) => (
                  <li key={idx}>
                    <a
                      href={link.href}
                      className="text-sm text-muted-foreground hover:text-primary transition-colors flex items-center gap-1 group"
                    >
                      <span className="group-hover:translate-x-1 transition-transform">{link.name}</span>
                    </a>
                  </li>
                ))}
              </ul>
            </div>

            {/* Legal Links */}
            <div>
              <h4 className="font-semibold text-foreground mb-4">Legal</h4>
              <ul className="space-y-3">
                {footerLinks.legal.map((link, idx) => (
                  <li key={idx}>
                    <a
                      href={link.href}
                      className="text-sm text-muted-foreground hover:text-primary transition-colors flex items-center gap-1 group"
                    >
                      <span className="group-hover:translate-x-1 transition-transform">{link.name}</span>
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Bottom Bar */}
          <div className="pt-8 border-t border-border/30">
            <div className="flex flex-col md:flex-row justify-between items-center gap-4">
              <div className="text-sm text-muted-foreground">
                <p>© {new Date().getFullYear()} DataHalo. All rights reserved.</p>
                <p className="text-xs mt-1">
                  Made with ❤️ for journalists, researchers, and truth-seekers worldwide.
                </p>
              </div>

              <div className="flex items-center gap-6 text-xs text-muted-foreground">
                <span className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                  All systems operational
                </span>
                <a href="#" className="hover:text-primary transition-colors">Status</a>
                <a href="#" className="hover:text-primary transition-colors">Changelog</a>
              </div>
            </div>
          </div>

          {/* Extra Info Bar */}
          <div className="mt-8 p-4 rounded-xl bg-gradient-to-r from-primary/5 via-accent/5 to-primary/5 border border-primary/20">
            <div className="flex flex-wrap items-center justify-center gap-6 text-xs text-muted-foreground">
              <span> Powered by NVIDIA AI</span>
              <span>•</span>
              <span>STATS: Real-time Analysis</span>
              <span>•</span>
              <span> Privacy First</span>
              <span>•</span>
              <span> Global Coverage</span>
              <span>•</span>
              <span> Research Ready</span>
            </div>
          </div>
        </motion.footer>
      </div>
    </section>
  );
};

export default Contact;