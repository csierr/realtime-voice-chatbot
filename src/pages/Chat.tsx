import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ArrowLeft, Send, Mic, MicOff } from "lucide-react";
import ChatMessage from "@/components/ChatMessage";
import VoiceIndicator from "@/components/VoiceIndicator";
import useWebSocket from "@/hooks/useWebSocket";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

const Chat = () => {
  const navigate = useNavigate();
  const { messages, sendMessage, isConnecting, audioQueue, setAudioQueue, isAudioFinished } = useWebSocket("ws://localhost:8000/ws");
  const [input, setInput] = useState("");
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);

  useEffect(() => {
    if (isAudioFinished && audioQueue.length > 0) {
      const audioBlob = new Blob(
        audioQueue.map((item) => {
          const byteCharacters = atob(item);
          const byteNumbers = new Array(byteCharacters.length);
          for (let i = 0; i < byteCharacters.length; i++) {
            byteNumbers[i] = byteCharacters.charCodeAt(i);
          }
          const byteArray = new Uint8Array(byteNumbers);
          return byteArray;
        }),
        { type: "audio/mpeg" }
      );
      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);
      audio.play();
      setAudioQueue([]);
    }
  }, [audioQueue, setAudioQueue, isAudioFinished]);

  const handleSendMessage = () => {
    if (!input.trim()) return;
    sendMessage(input);
    setInput("");
  };

  const toggleVoice = () => {
    setIsListening(!isListening);
    // Here you would integrate with your Realtime API
  };

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Header */}
      <header className="border-b border-border/50 bg-gradient-card shadow-card backdrop-blur-sm">
        <div className="max-w-4xl mx-auto px-4 py-5 flex items-center justify-between">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate("/")}
            className="gap-2 text-base"
          >
            <ArrowLeft className="w-5 h-5" />
            Back
          </Button>
          <h1 className="text-xl font-semibold text-foreground">Real-Time Assistant</h1>
          <div className="w-20"></div>
        </div>
      </header>

      {/* Chat Messages */}
      <main className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto px-4 py-6 space-y-4">
          {isConnecting && <p>Connecting to the server...</p>}
          {messages.map((message) => (
            <ChatMessage key={message.id} message={message} />
          ))}
        </div>
      </main>

      {/* Voice Indicator */}
      {(isListening || isSpeaking) && (
        <div className="max-w-4xl mx-auto px-4 py-2">
          <VoiceIndicator isListening={isListening} isSpeaking={isSpeaking} />
        </div>
      )}

      {/* Input Area */}
      <footer className="border-t border-border/50 bg-gradient-card shadow-card backdrop-blur-sm">
        <div className="max-w-4xl mx-auto px-4 py-5">
          <div className="flex gap-3">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSendMessage()}
              placeholder="Type your message..."
              className="flex-1 h-12 text-base bg-background/50 border-border/50"
            />
            <Button
              onClick={handleSendMessage}
              size="icon"
              className="bg-gradient-primary text-primary-foreground hover:opacity-90 hover:shadow-glow transition-all shadow-button w-12 h-12"
            >
              <Send className="w-5 h-5" />
            </Button>
            <Button
              onClick={toggleVoice}
              size="icon"
              variant={isListening ? "default" : "outline"}
              className={isListening ? "bg-accent text-accent-foreground shadow-glow w-12 h-12" : "w-12 h-12 border-border/50"}
            >
              {isListening ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
            </Button>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Chat;
