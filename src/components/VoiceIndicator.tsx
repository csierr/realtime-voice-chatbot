import { Mic, Volume2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface VoiceIndicatorProps {
  isListening: boolean;
  isSpeaking: boolean;
}

const VoiceIndicator = ({ isListening, isSpeaking }: VoiceIndicatorProps) => {
  return (
    <div className="flex items-center justify-center gap-3 py-3">
      <div
        className={cn(
          "flex items-center gap-3 px-6 py-3 rounded-full transition-all duration-300 shadow-glow",
          isListening && "bg-accent/20 border border-accent",
          isSpeaking && "bg-primary/20 border border-primary"
        )}
      >
        {isListening && (
          <>
            <Mic className="w-5 h-5 text-accent" />
            <div className="flex gap-1.5">
              <div className="w-1.5 h-5 bg-accent rounded-full animate-pulse"></div>
              <div className="w-1.5 h-5 bg-accent rounded-full animate-pulse delay-75"></div>
              <div className="w-1.5 h-5 bg-accent rounded-full animate-pulse delay-150"></div>
            </div>
            <span className="text-base text-accent font-medium">Listening...</span>
          </>
        )}
        {isSpeaking && (
          <>
            <Volume2 className="w-5 h-5 text-primary" />
            <div className="flex gap-1.5">
              <div className="w-1.5 h-5 bg-primary rounded-full animate-pulse"></div>
              <div className="w-1.5 h-5 bg-primary rounded-full animate-pulse delay-75"></div>
              <div className="w-1.5 h-5 bg-primary rounded-full animate-pulse delay-150"></div>
            </div>
            <span className="text-base text-primary font-medium">Speaking...</span>
          </>
        )}
      </div>
    </div>
  );
};

export default VoiceIndicator;
