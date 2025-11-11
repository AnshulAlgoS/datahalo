import React, { useState, useRef } from "react";
import { motion } from "framer-motion";
import { BadgeCheck, Copy, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import html2canvas from "html2canvas";

// VerifiedJournalistCard - a polished, badge-based verified card with loading and generated ID flow
export default function VerifiedJournalistCard() {
  const [loading, setLoading] = useState(false);
  const [progressText, setProgressText] = useState<string | null>(null);
  const [claimed, setClaimed] = useState(false);
  const [journalistId, setJournalistId] = useState<string | null>(null);

  const profileImage = "https://i.postimg.cc/W37XvjbF/images-13.jpg"; // user-provided image

  const cardRef = useRef<HTMLDivElement>(null); // existing card
  const idCardRef = useRef<HTMLDivElement>(null); // hidden professional ID card

  function startClaimFlow() {
    if (loading) return;
    setLoading(true);
    setProgressText("Initializing claim...");

    // sequence of progress updates
    const steps = [
      { text: "Verifying profile assets", delay: 700 },
      { text: "Checking citation & footprint", delay: 900 },
      { text: "Running credibility heuristics", delay: 1200 },
      { text: "Finalizing journalist ID", delay: 800 },
    ];

    let t = 0;
    steps.forEach((s) => {
      t += s.delay;
      setTimeout(() => setProgressText(s.text), t);
    });

    // finalize claim
    setTimeout(async () => {
      const id = generateId();
      setJournalistId(id);
      setProgressText(null);
      setLoading(false);
      setClaimed(true);

      // Download professional ID card
      if (idCardRef.current) {
        const canvas = await html2canvas(idCardRef.current, { scale: 3 });
        const dataURL = canvas.toDataURL("image/png");
        const link = document.createElement("a");
        link.href = dataURL;
        link.download = `${id}-journalist-id-card.png`;
        link.click();
      }
    }, t + 700);
  }

  function generateId() {
    return `JID-${Date.now().toString(36).slice(-6).toUpperCase()}`;
  }

  async function copyId() {
    if (!journalistId) return;
    try {
      await navigator.clipboard.writeText(journalistId);
    } catch (e) {
      console.warn("copy failed", e);
    }
  }

  return (
    <section aria-labelledby="cred-card" className="max-w-3xl mx-auto p-6">
      {/* EXISTING CARD */}
      <motion.div
        ref={cardRef}
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="relative rounded-2xl bg-gradient-to-br from-background/60 via-muted/10 to-background p-6 shadow-2xl border border-border/30 overflow-hidden"
      >
        <div
          className="absolute -inset-1 rounded-2xl pointer-events-none"
          style={{ filter: "blur(18px)", opacity: 0.06 }}
        />

        <div className="flex gap-6 items-center">
          <div className="relative w-28 h-28 rounded-xl overflow-hidden flex-shrink-0 ring-2 ring-primary/30">
            <img
              src={profileImage}
              alt="Palki Sharma Upadhyay"
              className="w-full h-full object-cover"
            />
            <div className="absolute -bottom-2 -right-2 bg-white/10 backdrop-blur-md rounded-full p-2 ring-1 ring-white/10">
              <BadgeCheck className="w-5 h-5 text-primary" />
            </div>
          </div>

          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h3
                  id="cred-card"
                  className="text-lg md:text-xl font-semibold leading-tight"
                >
                  Palki Sharma Upadhyay
                </h3>
                <p className="text-xs uppercase tracking-wider text-muted-foreground/90">
                  Senior Correspondent · Verified Journalist
                </p>
              </div>

              <div className="flex items-center gap-3">
                <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-sm font-medium ring-1 ring-primary/20">
                  <BadgeCheck className="w-4 h-4 text" />
                  Verified
                </span>
              </div>
            </div>

            <p className="mt-3 text-sm text-muted-foreground/90">
              Credibility metrics: tone balance, citation depth, engagement &
              authenticity — audited and summarized for transparency.
            </p>

            <div className="mt-4 grid grid-cols-2 gap-3 md:grid-cols-4">
              <Stat label="Tone Balance" value="92%" />
              <Stat label="Citation Depth" value="85%" />
              <Stat label="Engagement" value="88%" />
              <Stat label="Authenticity" value="90%" />
            </div>

            <div className="mt-6 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
              <div className="flex items-center gap-3">
                <div className="text-xs text-muted-foreground">Status</div>
                <div
                  className={`px-3 py-1 rounded-full text-sm font-medium ${
                    claimed
                      ? "bg-green-100 text-green-800 ring-1 ring-green-200"
                      : "bg-muted/10 text-muted-foreground ring-1 ring-border/20"
                  }`}
                >
                  {claimed ? "ID Claimed" : "Not Claimed"}
                </div>
              </div>

              <div className="flex items-center gap-3">
                <Button
                  onClick={startClaimFlow}
                  className="px-6 py-3 rounded-xl"
                  disabled={loading}
                >
                  {loading ? (
                    <span className="inline-flex items-center gap-2">
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Generating...
                    </span>
                  ) : claimed ? (
                    <span className="inline-flex items-center gap-2">Claimed</span>
                  ) : (
                    <span className="inline-flex items-center gap-2">
                      Claim Journalist ID
                    </span>
                  )}
                </Button>

                {claimed && journalistId && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="inline-flex items-center gap-2"
                  >
                    <div className="px-3 py-2 bg-background/60 ring-1 ring-border/20 rounded-lg text-sm font-mono">
                      {journalistId}
                    </div>
                    <button
                      onClick={copyId}
                      aria-label="Copy ID"
                      className="px-3 py-2 rounded-lg ring-1 ring-border/20 bg-muted/5 hover:bg-muted/10"
                    >
                      <Copy className="w-4 h-4" />
                    </button>
                  </motion.div>
                )}
              </div>
            </div>

            <div className="mt-4">
              {loading && (
                <div className="w-full rounded-xl p-3 bg-muted/5 ring-1 ring-border/10 flex items-center gap-3">
                  <Loader2 className="w-5 h-5 animate-spin text-primary" />
                  <div className="flex-1">
                    <div className="text-sm font-medium">{progressText}</div>
                    <div className="mt-1 h-2 bg-muted rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-primary to-accent"
                        style={{ width: "60%" }}
                      />
                    </div>
                  </div>
                </div>
              )}

              {!loading && !claimed && (
                <div className="mt-2 text-xs text-muted-foreground/80">
                  Want to claim this journalist's official ID? Click the button
                  to generate a verifiable, tamper-resistant ID (demo flow).
                </div>
              )}
            </div>
          </div>
        </div>
      </motion.div>

      {/* PROFESSIONAL ID CARD (HIDDEN) */}
      {claimed && journalistId && (
        <div className="absolute top-[-9999px]" ref={idCardRef}>
          <div className="w-[420px] h-[250px] bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 rounded-xl p-6 text-white shadow-lg relative font-sans">
            <div className="flex items-center gap-4">
              <img
                src={profileImage}
                alt="Profile"
                className="w-20 h-20 rounded-full ring-2 ring-white"
              />
              <div>
                <h2 className="text-lg font-bold">{journalistId}</h2>
                <p className="text-sm mt-1 font-medium">Palki Sharma Upadhyay</p>
                <p className="text-xs mt-1">Senior Correspondent</p>
              </div>
            </div>

            <div className="absolute top-4 right-4 flex items-center gap-1 text-xs uppercase tracking-wide">
              <BadgeCheck className="w-4 h-4" />
              Verified
            </div>

            <div className="absolute bottom-4 left-6 text-xs opacity-80">
              Digitally generated, verifiable ID.
            </div>

            <div className="absolute bottom-4 right-6 w-14 h-14 bg-white/20 rounded-full rotate-45" />
          </div>
        </div>
      )}
    </section>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="p-2 rounded-lg bg-background/5 border border-border/10 text-center">
      <div className="text-sm font-bold text-primary">{value}</div>
      <div className="text-[10px] uppercase tracking-wide text-muted-foreground mt-1">
        {label}
      </div>
    </div>
  );
}
