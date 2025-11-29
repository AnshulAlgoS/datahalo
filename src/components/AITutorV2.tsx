
// 🎓 WORLD'S BEST AI Media Literacy Tutor - Multi-Chat Edition
import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { 
  Loader2, Send, Bot, User, X, MessageCircle, Search, 
  Plus, Trash2, Edit2, Check, History, BookOpen, 
  Lightbulb, Target, ExternalLink, ChevronLeft, Menu,
  BarChart2, Theater, CheckCircle, Camera, FileSearch,
  Newspaper, Brain, AlertTriangle, Globe
} from "lucide-react";
import { toast } from "sonner";
import { useAuth } from "@/contexts/AuthContext";
import axios from "axios";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  web_search_used?: boolean;
  sources?: Array<{ title: string; url: string }>;
}

interface ChatSession {
  _id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

interface AITutorProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function AITutorV2({ isOpen, onClose }: AITutorProps) {
  const { currentUser } = useAuth();
  const [currentChatId, setCurrentChatId] = useState<string | null>(null);
  const [chats, setChats] = useState<ChatSession[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [showSidebar, setShowSidebar] = useState(true);
  const [editingChatId, setEditingChatId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);

  const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

  // Load user's chats when component opens
  useEffect(() => {
    if (isOpen && currentUser) {
      loadUserChats();
    }
  }, [isOpen, currentUser]);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const loadUserChats = async () => {
    if (!currentUser) return;

    setHistoryLoading(true);
    try {
      const response = await axios.get(`${API_URL}/ai-tutor/chats/${currentUser.uid}`);

      if (response.data.status === "success") {
        setChats(response.data.chats);
        
        // Load most recent chat if exists
        if (response.data.chats.length > 0 && !currentChatId) {
          loadChatMessages(response.data.chats[0]._id);
        } else if (response.data.chats.length === 0) {
          // Start with welcome message
          setMessages([{
            role: "assistant",
            content: "Hello! I'm your **AI Media Literacy Tutor**. I'm here to help you become a critical thinker and navigate the information landscape with confidence.\n\n**I can help you with:**\n\n• Media Bias & Objectivity\n• Propaganda Techniques\n• Fact-Checking Methods\n• Deepfakes & Manipulation\n• Source Evaluation\n• Narrative Analysis\n• Critical Thinking Skills\n\n**Try asking me:**\n• \"Teach me about confirmation bias\"\n• \"How do I spot fake news?\"\n• \"Give me examples of propaganda techniques\"\n• \"What is the SIFT method?\"\n\nI search the web to provide current, accurate information backed by reliable sources.",
            timestamp: new Date()
          }]);
        }
      }
    } catch (error) {
      console.error("Failed to load chats:", error);
    } finally {
      setHistoryLoading(false);
    }
  };

  const loadChatMessages = async (chatId: string) => {
    try {
      const response = await axios.get(`${API_URL}/ai-tutor/chat/${chatId}/messages`);

      if (response.data.status === "success") {
        const loadedMessages: Message[] = response.data.messages.map((msg: any) => ({
          role: msg.role,
          content: msg.content,
          timestamp: new Date(msg.timestamp),
          web_search_used: msg.web_search_used,
          sources: msg.sources
        }));

        setMessages(loadedMessages);
        setCurrentChatId(chatId);
        toast.success("Chat loaded!");
      }
    } catch (error) {
      console.error("Failed to load messages:", error);
      toast.error("Failed to load chat");
    }
  };

  const createNewChat = async () => {
    if (!currentUser) {
      toast.error("Please log in to create chats");
      return;
    }

    try {
      const response = await axios.post(`${API_URL}/ai-tutor/chat/create`, {
        user_id: currentUser.uid,
        title: "New Conversation"
      });

      if (response.data.status === "success") {
        const newChat: ChatSession = {
          _id: response.data.chat_id,
          title: response.data.title,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          message_count: 0
        };

        setChats([newChat, ...chats]);
        setCurrentChatId(response.data.chat_id);
        setMessages([{
          role: "assistant",
          content: "New conversation started! What would you like to learn about today?",
          timestamp: new Date()
        }]);
        toast.success("New chat created!");
      }
    } catch (error) {
      console.error("Failed to create chat:", error);
      toast.error("Failed to create new chat");
    }
  };

  const updateChatTitle = async (chatId: string, newTitle: string) => {
    try {
      await axios.put(`${API_URL}/ai-tutor/chat/title`, {
        chat_id: chatId,
        title: newTitle
      });

      setChats(chats.map(chat => 
        chat._id === chatId ? { ...chat, title: newTitle } : chat
      ));
      setEditingChatId(null);
      toast.success("Title updated!");
    } catch (error) {
      console.error("Failed to update title:", error);
      toast.error("Failed to update title");
    }
  };

  const deleteChat = async (chatId: string) => {
    if (!confirm("Delete this chat? This cannot be undone.")) return;

    try {
      await axios.delete(`${API_URL}/ai-tutor/chat/${chatId}`);

      setChats(chats.filter(chat => chat._id !== chatId));
      
      if (currentChatId === chatId) {
        setCurrentChatId(null);
        setMessages([]);
        
        // Load first available chat or show welcome
        if (chats.length > 1) {
          loadChatMessages(chats[0]._id);
        }
      }

      toast.success("Chat deleted!");
    } catch (error) {
      console.error("Failed to delete chat:", error);
      toast.error("Failed to delete chat");
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
      const response = await axios.post(`${API_URL}/ai-tutor`, {
        message: messageToSend,
        conversation_history: messages.slice(-8).map(m => ({
          role: m.role,
          content: m.content
        })),
        user_id: currentUser?.uid || null,
        chat_id: currentChatId,
        chat_title: messages.length === 1 ? messageToSend.slice(0, 50) : undefined
      });

      const assistantMessage: Message = {
        role: "assistant",
        content: response.data.response,
        timestamp: new Date(),
        web_search_used: response.data.context_used,
        sources: response.data.sources || []
      };

      setMessages((prev) => [...prev, assistantMessage]);
      
      // Update chat ID if new chat was created
      if (response.data.chat_id && !currentChatId) {
        setCurrentChatId(response.data.chat_id);
        // Reload chats to show the new one
        loadUserChats();
      }
      
      if (response.data.context_used) {
        toast.success("Enhanced with web search", { duration: 2000 });
      }
    } catch (error: any) {
      console.error("AI Tutor error:", error);
      toast.error("Failed to get response");
      
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

  const quickPrompts = [
    { icon: BarChart2, text: "What is media bias?" },
    { icon: Theater, text: "Teach me propaganda techniques" },
    { icon: CheckCircle, text: "How to fact-check effectively?" },
    { icon: Camera, text: "Explain deepfakes with examples" },
    { icon: FileSearch, text: "What is the SIFT method?" },
    { icon: Newspaper, text: "How to evaluate news sources?" }
  ];

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-background/95 backdrop-blur-sm md:flex md:items-center md:justify-center">
      <div className="w-full h-full md:w-[90vw] md:h-[85vh] md:max-w-7xl flex shadow-2xl md:rounded-lg overflow-hidden border border-primary/20">
        
        {/* Sidebar - Chat List */}
        <div className={`${showSidebar ? 'w-full md:w-80' : 'w-0'} bg-card border-r border-border transition-all duration-300 overflow-hidden flex flex-col`}>
          <div className="p-4 border-b border-border bg-card/80 backdrop-blur-sm">
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-lg font-bold flex items-center gap-2">
                <MessageCircle className="w-5 h-5 text-primary" />
                Your Chats
              </h2>
              <Button
                onClick={onClose}
                size="icon"
                variant="ghost"
                className="md:hidden"
              >
                <X className="w-5 h-5" />
              </Button>
            </div>
            <Button
              onClick={createNewChat}
              className="w-full bg-primary hover:bg-primary/90 text-primary-foreground"
              size="sm"
            >
              <Plus className="w-4 h-4 mr-2" />
              New Conversation
            </Button>
          </div>

          <ScrollArea className="flex-1 p-2">
            {historyLoading ? (
              <div className="flex items-center justify-center p-8">
                <Loader2 className="w-6 h-6 animate-spin text-primary" />
              </div>
            ) : chats.length === 0 ? (
              <div className="text-center p-4 text-muted-foreground text-sm">
                <BookOpen className="w-12 h-12 mx-auto mb-2 opacity-50" />
                <p>No conversations yet.</p>
                <p>Start your first one!</p>
              </div>
            ) : (
              <div className="space-y-1">
                {chats.map((chat) => (
                  <div
                    key={chat._id}
                    className={`p-3 rounded-lg cursor-pointer transition-all group ${
                      currentChatId === chat._id
                        ? 'bg-primary/10 border border-primary/30'
                        : 'hover:bg-accent/50'
                    }`}
                    onClick={() => loadChatMessages(chat._id)}
                  >
                    {editingChatId === chat._id ? (
                      <div className="flex items-center gap-2" onClick={(e) => e.stopPropagation()}>
                        <Input
                          value={editTitle}
                          onChange={(e) => setEditTitle(e.target.value)}
                          className="h-8 text-sm"
                          autoFocus
                          onKeyPress={(e) => {
                            if (e.key === "Enter") {
                              updateChatTitle(chat._id, editTitle);
                            }
                          }}
                        />
                        <Button
                          size="icon"
                          variant="ghost"
                          className="h-8 w-8"
                          onClick={() => updateChatTitle(chat._id, editTitle)}
                        >
                          <Check className="w-4 h-4" />
                        </Button>
                      </div>
                    ) : (
                      <>
                        <div className="flex items-start justify-between gap-2">
                          <div className="flex-1 min-w-0">
                            <p className="font-medium text-sm truncate">{chat.title}</p>
                            <p className="text-xs text-muted-foreground">
                              {chat.message_count} messages • {new Date(chat.updated_at).toLocaleDateString()}
                            </p>
                          </div>
                          <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                            <Button
                              size="icon"
                              variant="ghost"
                              className="h-7 w-7"
                              onClick={(e) => {
                                e.stopPropagation();
                                setEditingChatId(chat._id);
                                setEditTitle(chat.title);
                              }}
                            >
                              <Edit2 className="w-3 h-3" />
                            </Button>
                            <Button
                              size="icon"
                              variant="ghost"
                              className="h-7 w-7 text-destructive hover:text-destructive"
                              onClick={(e) => {
                                e.stopPropagation();
                                deleteChat(chat._id);
                              }}
                            >
                              <Trash2 className="w-3 h-3" />
                            </Button>
                          </div>
                        </div>
                      </>
                    )}
                  </div>
                ))}
              </div>
            )}
          </ScrollArea>
        </div>

        {/* Main Chat Area */}
        <div className="flex-1 flex flex-col bg-background">
          {/* Header */}
          <div className="p-4 border-b border-border bg-primary text-primary-foreground">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => setShowSidebar(!showSidebar)}
                  className="text-primary-foreground hover:bg-primary-foreground/20"
                >
                  {showSidebar ? <ChevronLeft className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
                </Button>
                <Bot className="w-6 h-6" />
                <div>
                  <h1 className="font-bold text-lg">AI Media Literacy Tutor</h1>
                  <p className="text-xs text-primary-foreground/80 flex items-center gap-1">
                    <Target className="w-3 h-3" />
                    Expert • Interactive • Web-Enhanced
                  </p>
                </div>
              </div>
              <Button
                onClick={onClose}
                size="icon"
                variant="ghost"
                className="text-primary-foreground hover:bg-primary-foreground/20 hidden md:flex"
              >
                <X className="w-5 h-5" />
              </Button>
            </div>
          </div>

          {/* Messages */}
          <ScrollArea ref={scrollRef} className="flex-1 p-4 md:p-6">
            <div className="max-w-4xl mx-auto space-y-6">
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`flex gap-4 ${
                    message.role === "user" ? "flex-row-reverse" : ""
                  }`}
                >
                  <Avatar className={message.role === "assistant" ? "bg-primary" : "bg-primary/80"}>
                    <AvatarFallback className="text-primary-foreground">
                      {message.role === "assistant" ? <Bot className="w-5 h-5" /> : <User className="w-5 h-5" />}
                    </AvatarFallback>
                  </Avatar>
                  <div
                    className={`flex-1 rounded-xl p-4 ${
                      message.role === "user"
                        ? "bg-primary/10 border border-primary/20"
                        : "bg-card border border-border"
                    }`}
                  >
                    <div className="prose prose-sm dark:prose-invert max-w-none">
                      <ReactMarkdown
                        remarkPlugins={[remarkGfm]}
                        components={{
                          h1: ({node, ...props}) => <h1 className="text-xl font-bold mt-4 mb-2" {...props} />,
                          h2: ({node, ...props}) => <h2 className="text-lg font-bold mt-3 mb-2" {...props} />,
                          h3: ({node, ...props}) => <h3 className="text-base font-bold mt-2 mb-1" {...props} />,
                          p: ({node, ...props}) => <p className="text-sm leading-relaxed mb-2" {...props} />,
                          ul: ({node, ...props}) => <ul className="list-disc list-inside mb-2 space-y-1" {...props} />,
                          ol: ({node, ...props}) => <ol className="list-decimal list-inside mb-2 space-y-1" {...props} />,
                          li: ({node, ...props}) => <li className="text-sm" {...props} />,
                          strong: ({node, ...props}) => <strong className="font-bold" {...props} />,
                          em: ({node, ...props}) => <em className="italic" {...props} />,
                          blockquote: ({node, ...props}) => <blockquote className="border-l-4 border-primary pl-4 italic my-2" {...props} />,
                          code: ({node, inline, ...props}: any) => 
                            inline ? (
                              <code className="bg-muted px-1 py-0.5 rounded text-xs" {...props} />
                            ) : (
                              <code className="block bg-muted p-2 rounded text-xs my-2 overflow-x-auto" {...props} />
                            ),
                          a: ({node, ...props}) => <a className="text-primary hover:underline" target="_blank" rel="noopener noreferrer" {...props} />,
                        }}
                      >
                        {message.content}
                      </ReactMarkdown>
                    </div>
                    
                    {/* Sources */}
                    {message.sources && message.sources.length > 0 && (
                      <div className="mt-3 pt-3 border-t border-border/50">
                        <p className="text-xs font-semibold mb-2 flex items-center gap-1 text-primary">
                          <Search className="w-3 h-3" />
                          Sources Used:
                        </p>
                        <div className="space-y-1">
                          {message.sources.map((source, i) => (
                            <a
                              key={i}
                              href={source.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="flex items-center gap-2 text-xs text-muted-foreground hover:text-primary transition-colors"
                            >
                              <ExternalLink className="w-3 h-3" />
                              <span className="truncate">{source.title}</span>
                            </a>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    <div className="flex items-center gap-2 mt-2 justify-end">
                      {message.web_search_used && (
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
                <div className="flex gap-4">
                  <Avatar className="bg-primary">
                    <AvatarFallback className="text-primary-foreground">
                      <Bot className="w-5 h-5" />
                    </AvatarFallback>
                  </Avatar>
                  <div className="flex-1 rounded-xl p-4 bg-card border border-border">
                    <div className="flex items-center gap-2">
                      <Loader2 className="w-4 h-4 animate-spin text-primary" />
                      <Brain className="w-4 h-4 text-primary animate-pulse" />
                      <span className="text-sm text-muted-foreground">Thinking...</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </ScrollArea>

          {/* Quick Prompts */}
          {messages.length <= 1 && !loading && (
            <div className="px-4 md:px-6 pb-2">
              <div className="max-w-4xl mx-auto">
                <p className="text-xs text-muted-foreground mb-2 flex items-center gap-1">
                  <Lightbulb className="w-3 h-3" />
                  Quick Start Ideas:
                </p>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                  {quickPrompts.map((prompt, index) => {
                    const IconComponent = prompt.icon;
                    return (
                      <Button
                        key={index}
                        variant="outline"
                        size="sm"
                        className="text-xs justify-start hover:bg-primary/10 hover:text-primary hover:border-primary/30 transition-all"
                        onClick={() => setInput(prompt.text)}
                      >
                        <IconComponent className="w-3 h-3 mr-2" />
                        <span className="truncate">{prompt.text}</span>
                      </Button>
                    );
                  })}
                </div>
              </div>
            </div>
          )}

          {/* Input */}
          <div className="p-4 md:p-6 border-t border-border bg-card/50">
            <div className="max-w-4xl mx-auto">
              <div className="flex gap-2">
                <Input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask me anything about media literacy..."
                  disabled={loading}
                  className="flex-1 bg-background"
                />
                <Button 
                  onClick={sendMessage} 
                  disabled={loading || !input.trim()}
                  className="bg-primary hover:bg-primary/90 text-primary-foreground"
                >
                  {loading ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Send className="w-4 h-4" />
                  )}
                </Button>
              </div>
              {!currentUser && (
                <p className="text-xs text-muted-foreground mt-2 text-center flex items-center justify-center gap-1">
                  <AlertTriangle className="w-3 h-3" />
                  Sign in to save your conversations across sessions
                </p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Floating Button to Open AI Tutor
export function AITutorButton({ onClick }: { onClick: () => void }) {
  return (
    <Button
      onClick={onClick}
      className="fixed bottom-6 right-6 z-40 rounded-full w-16 h-16 bg-primary hover:bg-primary/90 text-primary-foreground shadow-[0_0_40px_hsl(191_100%_50%_/_0.6)] hover:shadow-[0_0_60px_hsl(191_100%_50%_/_0.8)] transition-all animate-float"
      size="icon"
    >
      <div className="relative">
        <MessageCircle className="w-7 h-7" />
        <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-500 rounded-full border-2 border-background animate-pulse" />
      </div>
    </Button>
  );
}
