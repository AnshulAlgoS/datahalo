import { motion } from "framer-motion";
import { Database, Brain, Shield } from "lucide-react";

const steps = [
  {
    icon: Database,
    title: "Data Aggregation Layer",
    description: "APIs + scraping from platforms like X, LinkedIn, Medium, and major news outlets. Comprehensive data collection for complete analysis.",
  },
  {
    icon: Brain,
    title: "AI Credibility Engine",
    description: "Analyzes tone, bias, citation quality, and engagement patterns using advanced NLP models and sentiment analysis.",
  },
  {
    icon: Shield,
    title: "Blockchain Verification",
    description: "Writes hashed identity & credibility record to blockchain for immutable, transparent, and verifiable journalist profiles.",
  },
];

const HowItWorks = () => {
  return (
    <section id="how-it-works" className="relative min-h-screen flex items-center py-24 px-6 overflow-hidden">
      {/* Background effects */}
      <div className="absolute inset-0 bg-gradient-to-b from-background via-muted/20 to-background" />
      
      <div className="relative z-10 max-w-7xl mx-auto w-full">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="font-orbitron text-4xl md:text-6xl font-bold mb-6">
            How It <span className="text-primary">Works</span>
          </h2>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            Three powerful layers working together to ensure journalist credibility
          </p>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-8 relative">
          {/* Connection lines */}
          <div className="hidden md:block absolute top-1/2 left-0 right-0 h-0.5 bg-gradient-to-r from-transparent via-primary/50 to-transparent" />

          {steps.map((step, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.2 }}
              viewport={{ once: true }}
              className="relative group"
            >
              <div className="relative p-8 rounded-2xl bg-card/50 backdrop-blur-md border border-border/50 hover:border-primary/50 transition-all duration-500 h-full">
                {/* Glow effect */}
                <div className="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"
                  style={{ boxShadow: "0 0 40px hsl(var(--glow-cyan) / 0.3)" }} />
                
                {/* Icon */}
                <div className="relative mb-6 inline-flex p-4 rounded-xl bg-primary/10 border border-primary/30">
                  <step.icon className="w-8 h-8 text-primary" />
                </div>

                {/* Step number */}
                <div className="absolute top-8 right-8 font-orbitron text-6xl font-bold text-primary/10">
                  0{index + 1}
                </div>

                {/* Content */}
                <h3 className="text-2xl font-bold mb-4 text-foreground">{step.title}</h3>
                <p className="text-muted-foreground leading-relaxed">{step.description}</p>

                {/* Animated pulse */}
                <motion.div
                  animate={{ scale: [1, 1.1, 1] }}
                  transition={{ duration: 2, repeat: Infinity, delay: index * 0.3 }}
                  className="absolute -bottom-2 left-1/2 -translate-x-1/2 w-20 h-1 bg-primary/30 rounded-full blur-sm"
                />
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default HowItWorks;