import { motion } from "framer-motion";
import { Mail, Phone, Send } from "lucide-react";
import { Button } from "@/components/ui/button";

const contactMethods = [
  {
    icon: Phone,
    title: "Schedule a Call",
    description: "Book a discovery call to discuss your needs",
    cta: "Book Now",
  },
  {
    icon: Mail,
    title: "Send an Enquiry",
    description: "Prefer to share details in writing?",
    cta: "Contact Us",
  },
  {
    icon: Send,
    title: "Get Demo Access",
    description: "Try our platform with a free demo",
    cta: "Request Demo",
  },
];

const Contact = () => {
  return (
    <section id="contact" className="relative min-h-screen flex items-center py-24 px-6 overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0">
        <div className="absolute inset-0 bg-gradient-to-b from-background via-primary/5 to-background" />
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
                {/* Icon */}
                <div className="mb-6 inline-flex p-6 rounded-2xl bg-primary/10 border border-primary/30 group-hover:scale-110 transition-transform duration-300">
                  <method.icon className="w-12 h-12 text-primary" />
                </div>

                {/* Content */}
                <h3 className="text-2xl font-bold mb-3 text-foreground">{method.title}</h3>
                <p className="text-muted-foreground mb-6">{method.description}</p>

                {/* CTA Button */}
                <Button 
                  className="w-full bg-secondary hover:bg-secondary/90 text-secondary-foreground rounded-xl"
                  size="lg"
                >
                  {method.cta}
                </Button>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Footer */}
        <motion.footer
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          viewport={{ once: true }}
          className="pt-12 border-t border-border/50"
        >
          <div className="flex flex-col md:flex-row justify-between items-center gap-6">
            <div>
              <h3 className="font-orbitron text-3xl font-bold mb-2">
                <span className="text-primary">DataHalo</span>
              </h3>
              <p className="text-sm text-muted-foreground">
                Built with Trust. Powered by AI. Verified by Blockchain.
              </p>
            </div>

            <div className="flex flex-wrap justify-center gap-6 text-sm text-muted-foreground">
              <a href="#" className="hover:text-primary transition-colors">About</a>
              <a href="#" className="hover:text-primary transition-colors">API Docs</a>
              <a href="#" className="hover:text-primary transition-colors">Claim Profile</a>
              <a href="#" className="hover:text-primary transition-colors">Dashboard</a>
              <a href="#" className="hover:text-primary transition-colors">Privacy</a>
            </div>
          </div>

          <div className="mt-8 pt-6 border-t border-border/30 text-center text-sm text-muted-foreground">
            <p>© {new Date().getFullYear()} DataHalo. All rights reserved.</p>
          </div>
        </motion.footer>
      </div>
    </section>
  );
};

export default Contact;