import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";

const Dashboard = () => {
  return (
    <section id="dashboard" className="relative min-h-screen flex items-center py-24 px-6 overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0 bg-gradient-to-b from-background via-muted/10 to-background" />

      <div className="relative z-10 max-w-7xl mx-auto w-full">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="font-orbitron text-4xl md:text-6xl font-bold mb-6">
            Credibility <span className="text-primary">Dashboard</span>
          </h2>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            Real-time analytics and transparent metrics for journalist credibility
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="relative max-w-4xl mx-auto"
        >
          {/* Dashboard mockup */}
          <div className="relative p-8 rounded-3xl bg-card/30 backdrop-blur-xl border border-border/50 overflow-hidden">
            {/* Glow effect */}
            <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-transparent to-accent/10" />

            {/* Score meter */}
            <div className="relative text-center mb-12">
              <div className="inline-flex flex-col items-center gap-4 p-8 rounded-2xl bg-background/50 border border-primary/30">
                <span className="text-sm uppercase tracking-wider text-muted-foreground">Credibility Score</span>
                <div className="relative">
                  <motion.div
                    initial={{ scale: 0 }}
                    whileInView={{ scale: 1 }}
                    transition={{ duration: 0.8, type: "spring" }}
                    viewport={{ once: true }}
                    className="font-orbitron text-7xl font-bold text-primary"
                    style={{ textShadow: "0 0 30px hsl(var(--glow-cyan) / 0.5)" }}
                  >
                    87
                  </motion.div>
                  <span className="text-2xl text-muted-foreground">/100</span>
                </div>
                <div className="flex gap-2">
                  <div className="w-32 h-2 bg-muted rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      whileInView={{ width: "87%" }}
                      transition={{ duration: 1, delay: 0.3 }}
                      viewport={{ once: true }}
                      className="h-full bg-gradient-to-r from-primary to-accent"
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Metrics grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
              {[
                { label: "Tone Balance", value: "92%" },
                { label: "Citation Depth", value: "85%" },
                { label: "Engagement", value: "88%" },
                { label: "Authenticity", value: "90%" },
              ].map((metric, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.4, delay: 0.1 * index }}
                  viewport={{ once: true }}
                  className="p-4 rounded-xl bg-background/30 border border-border/30 text-center"
                >
                  <div className="text-2xl font-bold text-primary mb-1">{metric.value}</div>
                  <div className="text-xs text-muted-foreground uppercase tracking-wide">{metric.label}</div>
                </motion.div>
              ))}
            </div>

            {/* CTA */}
            <div className="text-center">
              <Button className="px-8 py-6 text-lg bg-primary hover:bg-primary/90 text-primary-foreground rounded-xl">
                Claim Your Journalist ID
              </Button>
            </div>
          </div>

          {/* Floating elements */}
          <motion.div
            animate={{ y: [0, -20, 0] }}
            transition={{ duration: 4, repeat: Infinity }}
            className="absolute -top-4 -right-4 w-24 h-24 bg-primary/20 rounded-full blur-2xl"
          />
          <motion.div
            animate={{ y: [0, 20, 0] }}
            transition={{ duration: 5, repeat: Infinity }}
            className="absolute -bottom-4 -left-4 w-32 h-32 bg-accent/20 rounded-full blur-2xl"
          />
        </motion.div>
      </div>
    </section>
  );
};

export default Dashboard;