// AI Tutor Chatbot Component with RAG & Persistent History
import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Loader2, Send, Bot, User, X, MessageCircle, Search, History } from "lucide-react";
import { toast } from "sonner";
import { useAuth } from "@/contexts/AuthContext";
import axios from "axios";

interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  contextUsed?: boolean;
}

interface AITutorProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function AITutor({ isOpen, onClose }: AITutorProps) {
  const { currentUser } = useAuth();
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: "Hello! I'm your AI Media Literacy Tutor with web search capabilities. I can help you understand media bias, propaganda techniques, fact-checking, and more. Ask me anything!",
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Load chat history when component opens
  useEffect(() => {
    if (isOpen && currentUser && messages.length === 1) {
      loadChatHistory();
    }
  }, [isOpen, currentUser]);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  // Load chat history from MongoDB
  const loadChatHistory = async () => {
    if (!currentUser) return;

    setHistoryLoading(true);
    try {
      const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
      const response = await axios.get(`${API_URL}/ai-tutor/history/${currentUser.uid}`);

      if (response.data.status === "success" && response.data.history.length > 0) {
        const loadedMessages: Message[] = [
          {
            role: "assistant",
            content: "Welcome back! I've loaded your previous conversation from MongoDB. Feel free to continue or start a new topic!",
            timestamp: new Date()
          }
        ];

        // Add history messages (already in correct format from MongoDB)
        response.data.history.forEach((msg: any) => {
          loadedMessages.push({
            role: msg.role,
            content: msg.content,
            timestamp: new Date(msg.timestamp)
          });
        });

        setMessages(loadedMessages);
        toast.success(`Loaded ${response.data.message_count} messages from chat history`);
        console.log(`✅ Loaded ${response.data.exchange_count} exchanges (${response.data.message_count} messages) from MongoDB`);
      }
    } catch (error: any) {
      console.error("Failed to load history from MongoDB:", error);
      // Silently fail - not critical, user can start new conversation
    } finally {
      setHistoryLoading(false);
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage: Message = {
      role: "user",
      content: input,
      timestamp: new Date()
    };

    setMessages((prev) => [...prev, userMessage]);
    const messageToSend = input;
    setInput("");
    setLoading(true);

    try {
      const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
      
      const response = await axios.post(`${API_URL}/ai-tutor`, {
        message: messageToSend,
        conversation_history: messages.slice(-5).map(m => ({
          role: m.role,
          content: m.content
        })),
        user_id: currentUser?.uid || null
      });

      const assistantMessage: Message = {
        role: "assistant",
        content: response.data.response,
        timestamp: new Date(),
        contextUsed: response.data.context_used
      };

      setMessages((prev) => [...prev, assistantMessage]);
      
      if (response.data.context_used) {
        toast.success("Answer enhanced with web search", { duration: 2000 });
      }
    } catch (error: any) {
      console.error("AI Tutor error:", error);
      toast.error("Failed to get response from AI tutor");
      
      const errorMessage: Message = {
        role: "assistant",
        content: "I apologize, but I'm having trouble connecting right now. Please try again in a moment.",
        timestamp: new Date()
      };
      
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const quickQuestions = [
    "What is media bias?",
    "How do I spot propaganda?",
    "Explain fact-checking techniques",
    "What are deepfakes?",
    "How do I evaluate sources?"
  ];

  const handleQuickQuestion = (question: string) => {
    setInput(question);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed bottom-4 right-4 z-50 w-96 max-w-[calc(100vw-2rem)]">
      <Card className="shadow-[0_0_40px_hsl(191_100%_50%_/_0.3)] border-primary/30 backdrop-blur-md bg-card/95">
        <CardHeader className="bg-primary text-primary-foreground rounded-t-lg relative overflow-hidden">
          {/* Animated glow effect */}
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,_hsl(191_100%_50%_/_0.3),_transparent_50%)] animate-glow-pulse" />
          <div className="relative flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Bot className="w-6 h-6 drop-shadow-[0_0_8px_hsl(191_100%_50%_/_0.8)]" />
              <div>
                <CardTitle className="text-lg font-bold">AI Media Literacy Tutor</CardTitle>
                <p className="text-xs text-primary-foreground/80 flex items-center gap-1 mt-0.5">
                  <Search className="w-3 h-3" />
                  Powered by RAG & Web Search
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              {currentUser && historyLoading && (
                <Loader2 className="w-4 h-4 animate-spin" />
              )}
              <Button
                variant="ghost"
                size="icon"
                onClick={onClose}
                className="text-primary-foreground hover:bg-primary-foreground/20"
              >
                <X className="w-5 h-5" />
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent className="p-0 bg-background/50">
          <ScrollArea ref={scrollRef} className="h-96 p-4">
            <div className="space-y-4">
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`flex gap-3 ${
                    message.role === "user" ? "flex-row-reverse" : ""
                  }`}
                >
                  <Avatar className={message.role === "assistant" ? "bg-primary" : "bg-primary/80"}>
                    <AvatarFallback className="text-primary-foreground">
                      {message.role === "assistant" ? <Bot className="w-5 h-5" /> : <User className="w-5 h-5" />}
                    </AvatarFallback>
                  </Avatar>
                  <div
                    className={`flex-1 rounded-lg p-3 ${
                      message.role === "user"
                        ? "bg-primary/10 border border-primary/20 text-right backdrop-blur-sm"
                        : "bg-card/80 border border-border/50 backdrop-blur-sm"
                    }`}
                  >
                    <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                    <div className="flex items-center gap-2 mt-1 justify-end">
                      {message.contextUsed && message.role === "assistant" && (
                        <Badge variant="outline" className="text-xs border-primary/30 text-primary">
                          <Search className="w-3 h-3 mr-1" />
                          Web Enhanced
                        </Badge>
                      )}
                      <p className="text-xs text-muted-foreground">
                        {message.timestamp.toLocaleTimeString()}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
              {loading && (
                <div className="flex gap-3">
                  <Avatar className="bg-primary">
                    <AvatarFallback className="text-primary-foreground">
                      <Bot className="w-5 h-5" />
                    </AvatarFallback>
                  </Avatar>
                  <div className="flex-1 rounded-lg p-3 bg-card/80 border border-border/50 backdrop-blur-sm">
                    <Loader2 className="w-5 h-5 animate-spin text-primary" />
                  </div>
                </div>
              )}
            </div>
          </ScrollArea>

          {messages.length === 1 && (
            <div className="px-4 pb-2 bg-background/50">
              <p className="text-xs text-muted-foreground mb-2">Quick Questions:</p>
              <div className="flex flex-wrap gap-2">
                {quickQuestions.map((question, index) => (
                  <Button
                    key={index}
                    variant="outline"
                    size="sm"
                    className="text-xs hover:bg-primary/10 hover:text-primary hover:border-primary/30 transition-all"
                    onClick={() => handleQuickQuestion(question)}
                  >
                    {question}
                  </Button>
                ))}
              </div>
            </div>
          )}

          <div className="p-4 border-t border-border/50 bg-background/50">
            <div className="flex gap-2">
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask me anything about media literacy..."
                disabled={loading}
                className="flex-1 bg-background/50 border-border/50 focus:border-primary/50"
              />
              <Button 
                onClick={sendMessage} 
                disabled={loading || !input.trim()}
                className="bg-primary hover:bg-primary/90 text-primary-foreground shadow-[0_0_15px_hsl(191_100%_50%_/_0.3)] hover:shadow-[0_0_20px_hsl(191_100%_50%_/_0.5)] transition-all"
              >
                {loading ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Send className="w-4 h-4" />
                )}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

// Floating Button to Open AI Tutor
export function AITutorButton({ onClick }: { onClick: () => void }) {
  return (
    <Button
      onClick={onClick}
      className="fixed bottom-4 right-4 z-40 rounded-full w-14 h-14 bg-primary hover:bg-primary/90 text-primary-foreground shadow-[0_0_30px_hsl(191_100%_50%_/_0.5)] hover:shadow-[0_0_40px_hsl(191_100%_50%_/_0.7)] transition-all animate-float"
      size="icon"
    >
      <MessageCircle className="w-6 h-6" />
    </Button>
  );
}
