import { motion } from "framer-motion";

export function HeroSection() {
  return (
    <motion.div
      className="text-center space-y-4"
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: "easeOut" }}
    >
      <h1
        className="font-serif text-4xl sm:text-5xl md:text-6xl text-[#2C2C2C] leading-tight font-semibold"
        style={{ fontFamily: "Crimson Text, Georgia, serif" }}
      >
        AI-Powered Presentation
        <br />
        Creation
      </h1>
      <p className="text-base sm:text-lg text-[#5A5A5A] max-w-xl mx-auto font-sans">
        Describe your presentation in natural language. Get a professional
        Google Slides deck instantly.
      </p>
    </motion.div>
  );
}
