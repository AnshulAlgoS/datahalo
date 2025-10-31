import { motion } from "framer-motion";
import { Scale, FileText, Volume2, Users, BarChart2, Plug } from "lucide-react";

const features = [
  {
    icon: Scale,
    title: "Bias & Sentiment Detection",
    description: "Advanced AI analysis of tone, perspective, and potential bias in journalistic content.",
  },
  {
    icon: FileText,
    title: "Citation & Fact Reliability",
    description: "Verify sources, cross-reference citations, and assess factual accuracy of reporting.",
  },
  {
    icon: Volume2,
    title: "Tone & Authenticity Check",
    description: "Evaluate writing consistency, authenticity markers, and potential ghostwriting patterns.",
  },
  {
    icon: Users,
    title: "Engagement Validity",
    description: "Distinguish genuine audience engagement from bot activity and manipulation.",
  },
  {
    icon: BarChart2,
    title: "Public Trust Dashboard",
    description: "Real-time credibility scores and transparent metrics accessible to everyone.",
  },
  {
    icon: Plug,
    title: "API Integration",
    description: "Seamless integration with news platforms, CMS systems, and social media.",
  },
];

const Features = () => {
  return (
    <section id="features" className="relative min-h-screen flex items-center py-24 px-6 overflow-hidden">
      {/* Background pattern */}
      <div className="absolute inset-0">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,hsl(var(--glow-cyan)/0.1),transparent_50%)]" />
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
            Powerful <span className="text-primary">Features</span>
          </h2>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            Comprehensive tools for verifying journalist credibility and content authenticity
          </p>
        </motion.div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, scale: 0.9 }}
              whileInView={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.4, delay: index * 0.1 }}
              viewport={{ once: true }}
              whileHover={{ y: -8 }}
              className="group relative p-6 rounded-2xl bg-card/40 backdrop-blur-md border border-border/50 hover:border-primary/50 transition-all duration-300 cursor-pointer"
            >
              {/* Gradient background on hover */}
              <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
              
              {/* Glow effect */}
              <div className="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                style={{ boxShadow: "0 0 30px hsl(var(--glow-cyan) / 0.2)" }} />

              <div className="relative">
                {/* Icon */}
                <div className="mb-4 inline-flex p-3 rounded-lg bg-primary/10 border border-primary/20 group-hover:border-primary/40 transition-colors">
                  <feature.icon className="w-6 h-6 text-primary" />
                </div>

                {/* Content */}
                <h3 className="text-xl font-bold mb-3 text-foreground group-hover:text-primary transition-colors">
                  {feature.title}
                </h3>
                <p className="text-muted-foreground leading-relaxed">
                  {feature.description}
                </p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Features;