import * as React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { HeroSection } from "@/components/HeroSection";
import { PromptInput } from "@/components/PromptInput";
import { ResultDisplay } from "@/components/ResultDisplay";
import { Loader2 } from "lucide-react";
import { generatePresentation } from "@/services/api";
import type { GeneratePresentationResponse } from "@/services/api";

const DOCS_URL = "http://localhost:8001/docs";
const GITHUB_URL = "https://github.com/sharathkum05/ppt_agent";

export function LandingPage() {
  const [prompt, setPrompt] = React.useState("");
  const [isGenerating, setIsGenerating] = React.useState(false);
  const [result, setResult] = React.useState<GeneratePresentationResponse | null>(null);
  const [error, setError] = React.useState<string | null>(null);

  const handleGenerate = React.useCallback(async () => {
    const trimmed = prompt.trim();
    if (trimmed.length < 10) return;
    setError(null);
    setIsGenerating(true);
    try {
      const data = await generatePresentation(trimmed);
      setResult(data);
    } catch (err) {
      let message: string | null = null;
      if (err && typeof err === "object" && "response" in err) {
        const data = (err as { response?: { data?: { detail?: unknown } } }).response?.data;
        const detail = data?.detail;
        if (typeof detail === "string") message = detail;
        else if (Array.isArray(detail) && detail[0]?.msg) message = detail[0].msg;
      }
      setError(
        message ?? "Failed to generate presentation. Please check your connection and try again."
      );
    } finally {
      setIsGenerating(false);
    }
  }, [prompt]);

  const handleViewPresentation = React.useCallback(() => {
    if (result?.shareable_link) {
      window.open(result.shareable_link, "_blank", "noopener,noreferrer");
    }
  }, [result]);

  const handleCreateAnother = React.useCallback(() => {
    setResult(null);
    setPrompt("");
    setError(null);
  }, []);

  return (
    <div className="min-h-screen h-screen max-h-screen flex flex-col bg-[#FAFAFA] overflow-hidden">
      <Header />
      <main
        className="flex-1 min-h-0 flex items-center justify-center px-4 sm:px-6 overflow-y-auto"
        role="main"
      >
        <div className="max-w-[700px] w-full py-6 sm:py-8 space-y-6 sm:space-y-8">
          <HeroSection />
          <AnimatePresence mode="wait">
            {result ? (
              <ResultDisplay
                key="result"
                result={result}
                onViewPresentation={handleViewPresentation}
                onCreateAnother={handleCreateAnother}
              />
            ) : (
              <motion.div
                key="form"
                className="space-y-6"
                initial={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                <PromptInput
                  value={prompt}
                  onChange={setPrompt}
                  onSubmit={handleGenerate}
                  isGenerating={isGenerating}
                  error={error}
                  disabled={isGenerating}
                />
                {isGenerating && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="flex flex-col items-center justify-center gap-3 py-4"
                    role="status"
                    aria-live="polite"
                  >
                    <Loader2
                      className="h-8 w-8 animate-spin text-[#5B8A72]"
                      aria-hidden
                    />
                    <p className="text-sm text-[#5A5A5A] font-sans">
                      Creating your presentation…
                    </p>
                  </motion.div>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </main>
      <Footer />
    </div>
  );
}

function Header() {
  return (
    <header
      className="shrink-0 flex items-center justify-between h-14 px-4 sm:px-6 border-b border-[#EEEEEE] bg-[#FAFAFA]"
      role="banner"
    >
      <a
        href="/"
        className="font-serif text-lg font-semibold text-[#2C2C2C] hover:text-[#5B8A72] transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#5B8A72] focus-visible:ring-offset-2 rounded"
        style={{ fontFamily: "Crimson Text, Georgia, serif" }}
      >
        PPT Agent
      </a>
      <nav
        className="flex items-center gap-6 font-sans text-sm text-[#5A5A5A]"
        aria-label="Main navigation"
      >
        <a
          href="#about"
          className="hover:text-[#2C2C2C] transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#5B8A72] focus-visible:ring-offset-2 rounded"
        >
          About
        </a>
        <a
          href={DOCS_URL}
          target="_blank"
          rel="noopener noreferrer"
          className="hover:text-[#2C2C2C] transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#5B8A72] focus-visible:ring-offset-2 rounded"
        >
          Docs
        </a>
        <a
          href={GITHUB_URL}
          target="_blank"
          rel="noopener noreferrer"
          className="hover:text-[#2C2C2C] transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#5B8A72] focus-visible:ring-offset-2 rounded"
        >
          GitHub
        </a>
      </nav>
    </header>
  );
}

function Footer() {
  return (
    <footer
      className="shrink-0 flex items-center justify-center h-12 px-4 border-t border-[#EEEEEE] bg-[#FAFAFA]"
      role="contentinfo"
    >
      <p className="text-xs text-[#9CA3AF] font-sans">
        Built with{" "}
        <a
          href="https://anthropic.com"
          target="_blank"
          rel="noopener noreferrer"
          className="text-[#5B8A72] hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#5B8A72] focus-visible:ring-offset-2 rounded"
        >
          Anthropic Claude
        </a>{" "}
        &{" "}
        <a
          href="https://developers.google.com/slides"
          target="_blank"
          rel="noopener noreferrer"
          className="text-[#5B8A72] hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#5B8A72] focus-visible:ring-offset-2 rounded"
        >
          Google Slides
        </a>
      </p>
    </footer>
  );
}
