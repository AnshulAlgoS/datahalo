import { motion } from "framer-motion";
import { Shield, TrendingUp, CheckCircle } from "lucide-react";

const impacts = [
  {
    icon: Shield,
    text: "Detect misinformation before it spreads",
  },
  {
    icon: TrendingUp,
    text: "Empower ethical journalism",
  },
  {
    icon: CheckCircle,
    text: "Make credibility transparent and verifiable",
  },
];

const Impact = () => {
  return (
    <section id="impact" className="relative min-h-screen flex items-center py-24 px-6 overflow-hidden">
      {/* Background effects */}
      <div className="absolute inset-0">
        <div className="absolute inset-0 bg-gradient-to-tr from-primary/5 via-transparent to-accent/5" />
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 60, repeat: Infinity, ease: "linear" }}
          className="absolute top-1/4 right-1/4 w-96 h-96 bg-primary/10 rounded-full blur-3xl"
        />
      </div>

      <div className="relative z-10 max-w-6xl mx-auto w-full">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="font-orbitron text-4xl md:text-6xl font-bold mb-6">
            Rebuilding Global <span className="text-primary">Trust in Media</span>
          </h2>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            Our mission is to restore faith in journalism through transparent, AI-powered credibility verification
          </p>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-8">
          {impacts.map((impact, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -30 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: index * 0.2 }}
              viewport={{ once: true }}
              className="relative group"
            >
              <div className="relative p-8 rounded-2xl bg-card/40 backdrop-blur-md border border-border/50 hover:border-primary/50 transition-all duration-300 h-full">
                {/* Vertical line indicator */}
                <div className="absolute left-0 top-0 bottom-0 w-1 bg-gradient-to-b from-primary via-accent to-transparent" />
                
                {/* Icon */}
                <div className="mb-6 inline-flex p-4 rounded-xl bg-primary/10 border border-primary/30">
                  <impact.icon className="w-8 h-8 text-primary" />
                </div>

                {/* Text */}
                <p className="text-xl font-semibold text-foreground leading-relaxed">
                  {impact.text}
                </p>

                {/* Animated underline */}
                <motion.div
                  initial={{ width: 0 }}
                  whileInView={{ width: "100%" }}
                  transition={{ duration: 0.8, delay: 0.3 + index * 0.2 }}
                  viewport={{ once: true }}
                  className="absolute bottom-0 left-0 h-0.5 bg-gradient-to-r from-primary to-transparent"
                />
              </div>
            </motion.div>
          ))}
        </div>

        {/* Stats */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          viewport={{ once: true }}
          className="mt-20 grid grid-cols-2 md:grid-cols-4 gap-8"
        >
          {[
            { value: "10K+", label: "Journalists Verified" },
            { value: "1M+", label: "Articles Analyzed" },
            { value: "99.2%", label: "Accuracy Rate" },
            { value: "50+", label: "Media Partners" },
          ].map((stat, index) => (
            <div key={index} className="text-center">
              <div className="font-orbitron text-4xl md:text-5xl font-bold text-primary mb-2">
                {stat.value}
              </div>
              <div className="text-sm text-muted-foreground uppercase tracking-wide">
                {stat.label}
              </div>
            </div>
          ))}
        </motion.div>
      </div>
    </section>
  );
};

export default Impact;