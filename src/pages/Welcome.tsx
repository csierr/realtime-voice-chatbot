import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { MessageCircle, Mic, Sparkles } from "lucide-react";

const Welcome = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-hero flex flex-col">
      {/* Hero Section */}
      <main className="flex-1 flex items-center justify-center px-4 py-12">
        <div className="max-w-4xl w-full text-center space-y-8 animate-in fade-in duration-700">
          {/* Icon */}
          <div className="flex justify-center">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-primary blur-3xl opacity-40 rounded-full"></div>
              <div className="relative bg-gradient-card p-8 rounded-3xl shadow-glow border border-primary/20">
                <Sparkles className="w-20 h-20 text-primary drop-shadow-glow" />
              </div>
            </div>
          </div>

          {/* Heading */}
          <div className="space-y-4">
            <h1 className="text-5xl md:text-6xl font-bold text-foreground leading-tight">
              Your Real-Time Chatbot
            </h1>
            <p className="text-xl md:text-2xl text-muted-foreground max-w-2xl mx-auto">
              Experience natural conversations with advanced AI. Chat via text or speak naturally—your choice.
            </p>
          </div>

          {/* Features */}
          <div className="grid md:grid-cols-2 gap-4 max-w-2xl mx-auto pt-4">
            <div className="bg-gradient-card p-6 rounded-2xl shadow-glow border border-border/50 backdrop-blur-sm">
              <MessageCircle className="w-10 h-10 text-primary mb-3 mx-auto drop-shadow-glow" />
              <h3 className="font-semibold text-foreground mb-2 text-lg">Text Chat</h3>
              <p className="text-sm text-muted-foreground">
                Type your questions and get instant, intelligent responses
              </p>
            </div>
            <div className="bg-gradient-card p-6 rounded-2xl shadow-glow border border-border/50 backdrop-blur-sm">
              <Mic className="w-10 h-10 text-accent mb-3 mx-auto drop-shadow-glow" />
              <h3 className="font-semibold text-foreground mb-2 text-lg">Voice Interaction</h3>
              <p className="text-sm text-muted-foreground">
                Speak naturally and hear responses in real-time
              </p>
            </div>
          </div>

          {/* CTA */}
          <div className="pt-4">
            <Button
              onClick={() => navigate("/chat")}
              size="lg"
              className="bg-gradient-primary text-primary-foreground hover:opacity-90 hover:shadow-glow transition-all shadow-button px-10 py-7 text-lg rounded-xl h-auto font-semibold"
            >
              Start Conversation
              <MessageCircle className="ml-2 w-6 h-6" />
            </Button>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="py-6 text-center text-sm text-muted-foreground">
        Powered by OpenAI Realtime API
      </footer>
    </div>
  );
};

export default Welcome;
