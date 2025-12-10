'use client';

import { useState, useRef, useEffect } from 'react';
import axios from 'axios';

interface Message {
  id: number;
  type: 'user' | 'ai';
  content: string;
  query?: string;
  timestamp: Date;
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 0,
      type: 'ai',
      content: '⚔️ Welcome to the Land of Dawn! I am your AI guide for Mobile Legends heroes. Ask me anything about heroes, roles, counters, lanes, and strategies!',
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState<any>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await axios.get('http://localhost:8000/stats');
      setStats(response.data);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage: Message = {
      id: messages.length,
      type: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await axios.post('http://localhost:8000/chat', {
        question: input,
      });

      const aiMessage: Message = {
        id: messages.length + 1,
        type: 'ai',
        content: response.data.answer,
        query: response.data.cypher_query,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, aiMessage]);
    } catch (error: any) {
      const errorMessage: Message = {
        id: messages.length + 1,
        type: 'ai',
        content: `❌ Connection Error: ${error.response?.data?.detail || 'Unable to connect to server. Please ensure the API server is running on port 8000.'}`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const sampleQuestions = [
    { icon: '🎯', text: 'List all marksman heroes', color: 'from-red-500/20 to-orange-500/20' },
    { icon: '🛡️', text: 'Show me all tank heroes', color: 'from-blue-500/20 to-cyan-500/20' },
    { icon: '⚡', text: 'Who is Layla?', color: 'from-purple-500/20 to-pink-500/20' },
    { icon: '⚔️', text: 'What heroes counter Miya?', color: 'from-yellow-500/20 to-red-500/20' },
    { icon: '📊', text: 'How many heroes are there?', color: 'from-green-500/20 to-teal-500/20' },
  ];

  const roleIcons: { [key: string]: string } = {
    'marksman': '🏹',
    'tank': '🛡️',
    'fighter': '⚔️',
    'mage': '🔮',
    'assassin': '🗡️',
    'support': '💫',
  };

  return (
    <div className="min-h-screen relative">
      {/* Animated background elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-ml-blue/10 rounded-full blur-3xl animate-pulse-slow"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-ml-accent/10 rounded-full blur-3xl animate-pulse-slow" style={{ animationDelay: '1s' }}></div>
      </div>

      {/* Header */}
      <header className="relative border-b-2 border-ml-accent/30 backdrop-blur-md bg-ml-primary/50 shadow-2xl">
        <div className="absolute inset-0 bg-gradient-to-r from-ml-blue/10 via-transparent to-ml-accent/10"></div>
        <div className="container mx-auto px-6 py-6 relative">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 rounded-full bg-gradient-to-br from-ml-accent via-yellow-500 to-ml-orange 
                            flex items-center justify-center shadow-ml animate-glow overflow-hidden">
                <img src="/mobile-legends-logo.png" alt="Mobile Legends Logo" className="w-full h-full object-cover" />
              </div>
              <div>
                <h1 className="text-4xl md:text-5xl font-heading font-bold glow-text bg-gradient-to-r from-ml-accent via-yellow-300 to-ml-accent bg-clip-text text-transparent">
                  MOBILE LEGENDS
                </h1>
                <p className="text-ml-cyan text-sm md:text-base font-semibold tracking-wide uppercase">
                  Knowledge Graph & RAG AI System
                </p>
              </div>
            </div>
            <div className="hidden md:flex gap-3 items-center">
              {stats && (
                <>
                  <div className="card-ml px-6 py-3 card-glow">
                    <div className="text-3xl font-bold text-ml-accent glow-text">{stats.total_heroes}</div>
                    <div className="text-xs text-ml-cyan uppercase tracking-wider">Heroes</div>
                  </div>
                  <div className="card-ml px-6 py-3 card-glow">
                    <div className="text-3xl font-bold text-ml-blue glow-text">{stats.total_relationships}</div>
                    <div className="text-xs text-ml-cyan uppercase tracking-wider">Relations</div>
                  </div>
                </>
              )}
              <a
                href="/draft"
                className="px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 rounded-xl shadow-lg hover:shadow-purple-500/50 transition-all hover:scale-105 flex items-center gap-2 border-2 border-purple-400/50"
              >
                <span className="text-2xl">🎯</span>
                <div>
                  <div className="text-white font-bold text-sm uppercase tracking-wider">Try Draft Pick →</div>
                  <div className="text-purple-200 text-xs">Hero Recommendations</div>
                </div>
              </a>
            </div>
          </div>
        </div>
        {/* Shine effect */}
        <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-ml-accent to-transparent"></div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-6 max-w-7xl relative">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 min-h-[calc(100vh-180px)]">
          {/* Sidebar */}
          <div className="lg:col-span-1 space-y-4 animate-slideIn overflow-y-auto max-h-[calc(100vh-200px)]">
            {/* Sample Questions */}
            <div className="card-ml card-glow">
              <div className="flex items-center gap-2 mb-4">
                <span className="text-2xl">✨</span>
                <h3 className="text-xl font-bold text-ml-accent uppercase tracking-wide">Quick Actions</h3>
              </div>
              <div className="space-y-2">
                {sampleQuestions.map((q, idx) => (
                  <button
                    key={idx}
                    onClick={() => setInput(q.text)}
                    className={`w-full text-left px-4 py-3 text-sm bg-gradient-to-r ${q.color}
                             hover:bg-gradient-to-r hover:from-ml-accent/30 hover:to-ml-blue/30
                             rounded-xl transition-all text-ml-light border border-ml-blue/30
                             hover:border-ml-accent hover:shadow-ml-glow transform hover:scale-105
                             flex items-center gap-3 group`}
                  >
                    <span className="text-xl group-hover:scale-125 transition-transform">{q.icon}</span>
                    <span className="font-medium">{q.text}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Hero Roles Stats */}
            {stats && (
              <div className="card-ml card-glow">
                <div className="flex items-center gap-2 mb-4">
                  <span className="text-2xl">👥</span>
                  <h3 className="text-xl font-bold text-ml-accent uppercase tracking-wide">Hero Roles</h3>
                </div>
                <div className="space-y-3">
                  {stats.heroes_by_role?.slice(0, 6).map((role: any, idx: number) => (
                    <div key={idx} className="flex items-center justify-between p-3 rounded-lg
                                              bg-gradient-to-r from-ml-darker/50 to-transparent
                                              border border-ml-blue/20 hover:border-ml-accent/50
                                              transition-all group">
                      <div className="flex items-center gap-2 flex-1 min-w-0">
                        <span className="text-lg flex-shrink-0">{roleIcons[role.role] || '⭐'}</span>
                        <span className="text-ml-light/90 capitalize font-medium group-hover:text-ml-accent transition-colors text-sm truncate">
                          {role.role}
                        </span>
                      </div>
                      <span className="stat-badge flex-shrink-0">
                        <span className="text-ml-accent font-bold text-base">{role.count}</span>
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Chat Area */}
          <div className="lg:col-span-3 flex flex-col rounded-2xl border-2 border-ml-accent/30 
                         bg-ml-primary/30 backdrop-blur-md overflow-hidden shadow-2xl card-glow animate-fadeIn
                         min-h-[500px] max-h-[calc(100vh-200px)]">
            {/* Chat Header */}
            <div className="bg-gradient-to-r from-ml-primary via-ml-secondary to-ml-primary border-b-2 border-ml-accent/30 p-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-ml-cyan to-ml-blue 
                              flex items-center justify-center shadow-ml-glow animate-pulse">
                  <span className="text-xl">🤖</span>
                </div>
                <div>
                  <h2 className="text-lg font-bold text-ml-accent">AI Assistant</h2>
                  <p className="text-xs text-ml-cyan">Ready to help you explore heroes</p>
                </div>
                <div className="ml-auto flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-ml-green animate-pulse"></div>
                  <span className="text-xs text-ml-green font-semibold">Online</span>
                </div>
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-hero-pattern">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'} animate-fadeIn`}
                >
                  <div className={message.type === 'user' ? 'message-user' : 'message-ai'}>
                    <p className="whitespace-pre-wrap text-base leading-relaxed">{message.content}</p>
                    {message.query && (
                      <details className="mt-3 text-xs opacity-80">
                        <summary className="cursor-pointer hover:text-ml-accent transition-colors font-semibold flex items-center gap-2">
                          <span>🔍</span> View Cypher Query
                        </summary>
                        <code className="block mt-2 p-3 bg-ml-darker/70 rounded-lg border border-ml-blue/30 font-mono text-ml-cyan">
                          {message.query}
                        </code>
                      </details>
                    )}
                  </div>
                </div>
              ))}
              {loading && (
                <div className="flex justify-start animate-fadeIn">
                  <div className="message-ai">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 bg-ml-accent rounded-full loading-dot"></div>
                      <div className="w-3 h-3 bg-ml-blue rounded-full loading-dot"></div>
                      <div className="w-3 h-3 bg-ml-cyan rounded-full loading-dot"></div>
                      <span className="ml-2 text-sm text-ml-light/70">AI is thinking...</span>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="p-4 bg-gradient-to-r from-ml-primary via-ml-secondary to-ml-primary 
                          border-t-2 border-ml-accent/30 backdrop-blur-md">
              <div className="flex gap-3">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask about heroes, roles, counters, strategies..."
                  className="input-ml"
                  disabled={loading}
                />
                <button
                  onClick={sendMessage}
                  disabled={loading || !input.trim()}
                  className="btn-ml disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap
                           flex items-center gap-2 min-w-[120px] justify-center"
                >
                  {loading ? (
                    <>
                      <div className="w-5 h-5 border-2 border-ml-darker border-t-transparent rounded-full animate-spin"></div>
                      <span>Wait</span>
                    </>
                  ) : (
                    <>
                      <span>Send</span>
                    </>
                  )}
                </button>
              </div>
              <p className="text-xs text-ml-light/50 mt-2 text-center">
                Knowledge Graph & RAG AI System
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
