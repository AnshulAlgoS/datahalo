import { motion } from "framer-motion";
import { Database, Brain, BarChart3, Sparkles, Target, Shield } from "lucide-react";

const steps = [
  {
    icon: Database,
    title: "Multi-Source Data Intelligence",
    description:
      "Aggregates journalist profiles from X, LinkedIn, Medium, and news outlets. Scrapes articles with verified citations. NEW: URL-based narrative analysis finds related coverage across 100+ sources in real-time.",
  },
  {
    icon: Brain,
    title: "AI-Powered Deep Analysis",
    description:
      "NVIDIA AI analyzes tone, bias, political leanings, and evidence quality. NEW: Article-level insights extract key points, detect narrative framing, identify missing context, and reveal potential manipulation tactics.",
  },
  {
    icon: Shield,
    title: "Halo Score™ Transparency Metric",
    description:
      "Revolutionary 5-factor score (Reach, Engagement, Transparency, Work Quality, Resonance) replaces traditional credibility scoring. Evidence-based, no guessing—uses actual article citations and verifiable metrics.",
  },
  {
    icon: Target,
    title: "Narrative Timeline Tracking",
    description:
      "Track how stories evolve across time and outlets. Detect coordinated timing, source clustering, sentiment uniformity, and sudden spikes. Visualize manipulation indicators with detailed explanations.",
  },
  {
    icon: Sparkles,
    title: "Smart Research Export",
    description:
      "Export comprehensive analysis with academic citations for UPSC prep, dissertation research, and media literacy studies. Includes methodology notes, data quality metrics, and recommended actions.",
  },
  {
    icon: BarChart3,
    title: "Interactive Dashboards",
    description:
      "Beautiful visualizations show sentiment trends, source diversity, timeline heatmaps, and narrative clusters. Auto-detects localhost vs production. Mobile-responsive with real-time updates.",
  },
];

const HowItWorks = () => {
  return (
    <section
      id="how-it-works"
      className="relative min-h-screen flex items-center py-24 px-6 overflow-hidden"
    >
      {/* Background effects */}
      <div className="absolute inset-0 bg-gradient-to-b from-background via-muted/20 to-background" />
      
      {/* Animated background blobs */}
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
            Six powerful layers combining AI analysis, real-time data aggregation, and transparency metrics
            for comprehensive media understanding.
          </p>
          <div className="mt-6 flex items-center justify-center gap-6 text-sm">
            <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/30">
              <Sparkles className="w-4 h-4 text-primary" />
              <span className="font-semibold">NEW: URL Narrative Analysis</span>
            </div>
            <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/30">
              <Shield className="w-4 h-4 text-primary" />
              <span className="font-semibold">NEW: Halo Score™</span>
            </div>
          </div>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-8 relative">
          {/* Connection lines */}
          <div className="hidden md:block absolute top-1/3 left-0 right-0 h-0.5 bg-gradient-to-r from-transparent via-primary/50 to-transparent" />
          <div className="hidden md:block absolute top-2/3 left-0 right-0 h-0.5 bg-gradient-to-r from-transparent via-primary/50 to-transparent" />

          {steps.map((step, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.15 }}
              viewport={{ once: true }}
              className="relative group"
            >
              <div className="relative p-8 rounded-2xl bg-card/50 backdrop-blur-md border border-border/50 hover:border-primary/50 transition-all duration-500 h-full flex flex-col">
                {/* Glow effect */}
                <div
                  className="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"
                  style={{
                    boxShadow: "0 0 40px hsl(var(--glow-cyan) / 0.3)",
                  }}
                />

                {/* Icon */}
                <div className="relative mb-6 inline-flex p-4 rounded-xl bg-primary/10 border border-primary/30 group-hover:scale-110 transition-transform duration-300">
                  <step.icon className="w-8 h-8 text-primary" />
                </div>

                {/* Step number */}
                <div className="absolute top-8 right-8 font-orbitron text-6xl font-bold text-primary/10 group-hover:text-primary/20 transition-colors">
                  0{index + 1}
                </div>

                {/* Content */}
                <h3 className="text-2xl font-bold mb-4 text-foreground">
                  {step.title}
                </h3>
                <p className="text-muted-foreground leading-relaxed flex-1">
                  {step.description}
                </p>

                {/* Animated pulse */}
                <motion.div
                  animate={{ scale: [1, 1.1, 1], opacity: [0.5, 1, 0.5] }}
                  transition={{
                    duration: 2,
                    repeat: Infinity,
                    delay: index * 0.3,
                  }}
                  className="absolute -bottom-2 left-1/2 -translate-x-1/2 w-20 h-1 bg-primary/30 rounded-full blur-sm"
                />
              </div>
            </motion.div>
          ))}
        </div>

        {/* Use Cases Section */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          viewport={{ once: true }}
          className="mt-20 p-8 rounded-2xl bg-gradient-to-br from-primary/5 via-accent/5 to-primary/5 border border-primary/20"
        >
          <h3 className="text-2xl font-bold mb-6 text-center">
            Built For Everyone
          </h3>
          <div className="grid md:grid-cols-4 gap-6">
            {[
              {
                title: "NEWS: General Public",
                desc: "Understand media bias and identify manipulation"
              },
              {
                title: "📚 Students",
                desc: "UPSC/exam prep with current affairs analysis"
              },
              {
                title: "🔬 Researchers",
                desc: "Export data for academic studies with citations"
              },
              {
                title: "🎓 Educators",
                desc: "Teach media literacy and critical thinking"
              }
            ].map((useCase, idx) => (
              <div
                key={idx}
                className="p-4 rounded-xl bg-card/50 backdrop-blur-sm border border-border/50 hover:border-primary/50 transition-all"
              >
                <h4 className="font-bold mb-2">{useCase.title}</h4>
                <p className="text-sm text-muted-foreground">{useCase.desc}</p>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Features Highlight */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.6 }}
          viewport={{ once: true }}
          className="mt-12 text-center"
        >
          <div className="inline-flex flex-wrap items-center justify-center gap-4">
            {[
              "CHECK: AI-Powered Analysis",
              "CHECK: Real-Time Updates",
              "CHECK: Manipulation Detection",
              "CHECK: Export for Research",
              "CHECK: Mobile Responsive",
              "CHECK: Open Source"
            ].map((feature, idx) => (
              <div
                key={idx}
                className="px-4 py-2 rounded-full bg-card/50 border border-border/50 text-sm font-medium"
              >
                {feature}
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default HowItWorks;