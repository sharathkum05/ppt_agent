import * as React from "react";
import { motion } from "framer-motion";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

const MIN_PROMPT_LENGTH = 10;
const PLACEHOLDER =
  "e.g., Create a 5-slide presentation about renewable energy covering solar, wind, hydro, benefits, and future outlook";

interface PromptInputProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  isGenerating: boolean;
  error: string | null;
  disabled?: boolean;
}

export function PromptInput({
  value,
  onChange,
  onSubmit,
  isGenerating,
  error,
  disabled = false,
}: PromptInputProps) {
  const isValid = value.trim().length >= MIN_PROMPT_LENGTH;
  const textareaRef = React.useRef<HTMLTextAreaElement>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!isValid || isGenerating || disabled) return;
    onSubmit();
  };

  return (
    <motion.form
      className="space-y-4"
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.1, ease: "easeOut" }}
      onSubmit={handleSubmit}
    >
      <div className="relative">
        <Textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={PLACEHOLDER}
          disabled={isGenerating || disabled}
          aria-label="Presentation prompt"
          aria-invalid={!!error}
          aria-describedby={error ? "prompt-error" : undefined}
          className={cn(
            "min-h-[120px] max-h-[150px] resize-none rounded-xl border border-[#E5E5E5] bg-white px-4 py-3 text-[#2C2C2C] placeholder:text-[#9CA3AF] transition-shadow duration-200",
            "focus-visible:ring-2 focus-visible:ring-[#5B8A72]/30 focus-visible:border-[#5B8A72] focus-visible:shadow-md focus-visible:shadow-[#5B8A72]/10",
            "disabled:opacity-60 disabled:cursor-not-allowed"
          )}
          rows={5}
        />
        <div
          className="absolute bottom-3 right-4 text-xs text-[#9CA3AF] font-sans tabular-nums"
          aria-live="polite"
        >
          {value.length > 0 && `${value.length} characters`}
        </div>
      </div>

      {error && (
        <motion.p
          id="prompt-error"
          role="alert"
          className="text-sm text-red-600 font-sans"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          {error}
        </motion.p>
      )}

      <Button
        type="submit"
        disabled={!isValid || isGenerating || disabled}
        className={cn(
          "w-full sm:w-auto min-w-[200px] rounded-xl py-6 px-8 text-base font-medium transition-all duration-200",
          "bg-[#5B8A72] hover:bg-[#4a7560] hover:scale-[1.02] active:scale-[0.98]",
          "text-white shadow-sm hover:shadow-md",
          "focus-visible:ring-2 focus-visible:ring-[#5B8A72] focus-visible:ring-offset-2",
          "disabled:opacity-50 disabled:pointer-events-none disabled:hover:scale-100"
        )}
        aria-busy={isGenerating}
        aria-label={isGenerating ? "Generating presentation" : "Generate presentation"}
      >
        {isGenerating ? (
          <>
            <Loader2 className="h-5 w-5 animate-spin" aria-hidden />
            <span>Generating…</span>
          </>
        ) : (
          "Generate Presentation"
        )}
      </Button>
    </motion.form>
  );
}
