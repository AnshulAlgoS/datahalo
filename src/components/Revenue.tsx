import { motion } from "framer-motion";
import { Building2, Plug2, Link } from "lucide-react";

const revenueStreams = [
  {
    icon: Building2,
    title: "Subscription Plans",
    subtitle: "Media Houses",
    description: "Tiered access for news organizations to verify their journalists and integrate credibility scores.",
  },
  {
    icon: Plug2,
    title: "API-as-a-Service",
    subtitle: "Platform Integrations",
    description: "Seamless API integration for social media platforms, CMS systems, and news aggregators.",
  },
  {
    icon: Link,
    title: "Blockchain Verification",
    subtitle: "Individual Journalists",
    description: "One-time and recurring fees for blockchain-verified journalist identity and credibility badges.",
  },
];

const Revenue = () => {
  return (
    <section id="revenue" className="relative min-h-screen flex items-center py-24 px-6 overflow-hidden">
      {/* Background */}
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
            Revenue <span className="text-primary">Model</span>
          </h2>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            Sustainable and scalable monetization through multiple revenue streams
          </p>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-8">
          {revenueStreams.map((stream, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.2 }}
              viewport={{ once: true }}
              className="group relative"
            >
              <div className="relative p-8 rounded-2xl bg-card/50 backdrop-blur-md border border-border/50 hover:border-primary/50 transition-all duration-500 h-full">
                {/* Corner accent */}
                <div className="absolute top-0 right-0 w-20 h-20 bg-gradient-to-br from-primary/20 to-transparent rounded-bl-3xl" />
                
                {/* Icon */}
                <div className="mb-6 inline-flex p-4 rounded-xl bg-primary/10 border border-primary/30">
                  <stream.icon className="w-8 h-8 text-primary" />
                </div>

                {/* Content */}
                <h3 className="text-2xl font-bold mb-2 text-foreground">{stream.title}</h3>
                <p className="text-primary font-semibold mb-4">{stream.subtitle}</p>
                <p className="text-muted-foreground leading-relaxed">{stream.description}</p>

                {/* Trust badge */}
                <div className="mt-6 inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-primary/5 border border-primary/20">
                  <div className="w-2 h-2 rounded-full bg-primary animate-pulse" />
                  <span className="text-sm text-primary font-medium">Verified Model</span>
                </div>

                {/* Glow on hover */}
                <div className="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"
                  style={{ boxShadow: "0 0 40px hsl(var(--glow-cyan) / 0.2)" }} />
              </div>
            </motion.div>
          ))}
        </div>

        {/* Tech stack section */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          viewport={{ once: true }}
          className="mt-20"
        >
          <h3 className="font-orbitron text-3xl font-bold text-center mb-12">
            Powered by <span className="text-primary">Leading Technologies</span>
          </h3>
          
          <div className="flex flex-wrap justify-center gap-6">
            {["React", "FastAPI", "Python NLP", "BERT", "MongoDB", "Ethereum", "Polygon", "HuggingFace"].map((tech, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, scale: 0.8 }}
                whileInView={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
                viewport={{ once: true }}
                whileHover={{ scale: 1.1, rotate: 5 }}
                className="px-6 py-3 rounded-xl bg-card/40 backdrop-blur-md border border-primary/30 hover:border-primary/60 transition-all duration-300"
              >
                <span className="font-semibold text-foreground">{tech}</span>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default Revenue;