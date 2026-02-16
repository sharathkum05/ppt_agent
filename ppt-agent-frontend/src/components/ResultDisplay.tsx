import { motion } from "framer-motion";
import { Check, ExternalLink, PlusCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import type { GeneratePresentationResponse } from "@/services/api";

interface ResultDisplayProps {
  result: GeneratePresentationResponse;
  onViewPresentation: () => void;
  onCreateAnother: () => void;
}

export function ResultDisplay({
  result,
  onViewPresentation,
  onCreateAnother,
}: ResultDisplayProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: "easeOut" }}
      className="w-full max-w-xl mx-auto"
    >
      <Card className="rounded-2xl border border-[#E5E5E5] bg-white shadow-lg shadow-[#2C2C2C]/5 overflow-hidden">
        <CardContent className="p-6 sm:p-8 space-y-6">
          <div className="flex items-center gap-3">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: "spring", stiffness: 300, damping: 20, delay: 0.1 }}
              className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-[#5B8A72] text-white"
              aria-hidden
            >
              <Check className="h-5 w-5" strokeWidth={2.5} />
            </motion.div>
            <div>
              <h2 className="font-serif text-xl sm:text-2xl font-semibold text-[#2C2C2C]">
                Presentation ready
              </h2>
              <p className="text-sm text-[#5A5A5A] font-sans">
                {result.slide_count} slide{result.slide_count !== 1 ? "s" : ""} created
              </p>
            </div>
          </div>

          <div className="rounded-xl bg-[#FAFAFA] border border-[#EEEEEE] px-4 py-3">
            <p className="text-xs font-medium text-[#5A5A5A] uppercase tracking-wider font-sans mb-1">
              Title
            </p>
            <p className="font-serif text-lg text-[#2C2C2C] font-medium">
              {result.title}
            </p>
          </div>

          <div className="flex flex-col sm:flex-row gap-3">
            <Button
              onClick={onViewPresentation}
              className={cn(
                "flex-1 rounded-xl py-6 font-medium transition-all duration-200",
                "bg-[#5B8A72] hover:bg-[#4a7560] hover:scale-[1.02] active:scale-[0.98]",
                "text-white shadow-sm hover:shadow-md",
                "focus-visible:ring-2 focus-visible:ring-[#5B8A72] focus-visible:ring-offset-2"
              )}
              aria-label="Open presentation in Google Slides"
            >
              <ExternalLink className="h-4 w-4 shrink-0" />
              View Presentation
            </Button>
            <Button
              variant="outline"
              onClick={onCreateAnother}
              className={cn(
                "flex-1 rounded-xl py-6 font-medium border-[#E5E5E5] text-[#2C2C2C]",
                "hover:bg-[#F5F5F5] hover:scale-[1.02] active:scale-[0.98]",
                "focus-visible:ring-2 focus-visible:ring-[#5B8A72] focus-visible:ring-offset-2"
              )}
              aria-label="Create another presentation"
            >
              <PlusCircle className="h-4 w-4 shrink-0" />
              Create Another
            </Button>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
